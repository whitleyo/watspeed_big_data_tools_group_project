import torch
from torch.utils.data import Dataset
from sklearn.model_selection import TimeSeriesSplit, train_test_split
import random
from pymongo import MongoClient
from datetime import datetime
import os

class BioRxivDataset(Dataset):
    def __init__(self, 
             mongo_uri="mongodb://localhost:27017", 
             db_name="biorxiv", 
             collection_name="abstracts",
             subset_query=None,
             stream_mongo=False,
             indices=None):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.stream_mongo = stream_mongo
        self.transform = None
        self.transformed_data = None

        # Apply subset query
        self.subset_query = subset_query if subset_query else {}

        if self.stream_mongo:
            cursor = self.collection.find(self.subset_query, {"_id": 1, "date": 1}).sort("date", 1)
            all_ids = [doc["_id"] for doc in cursor]
            if not all_ids:
                raise ValueError("No data found in the specified MongoDB collection.")
            self.ids = [all_ids[i] for i in indices] if indices else all_ids
            self.data = None
        else:
            all_data = list(self.collection.find(self.subset_query, {"_id": 1, "doi": 1, "abstract": 1, "date": 1}).sort("date", 1))
            for doc in all_data:
                if "date" not in doc:
                    raise ValueError("Each document must contain a 'date' field.")
                if "abstract" not in doc:
                    raise ValueError("Each document must contain an 'abstract' field.")
            if not all_data:
                raise ValueError("No data found in the specified MongoDB collection.")
            # if indices:
            #     print(f"Using indices")
            self.data = [all_data[i] for i in indices] if indices else all_data
            assert len(self.data) > 0, "No data found in the specified MongoDB collection."
            self.ids = None

    def __len__(self):
        if self.transformed_data is not None:
            return len(self.transformed_data)
        return len(self.ids) if self.stream_mongo else len(self.data)

    def map(self, func, batched=False, lazy=False, **kwargs):
        batch_size = kwargs.get("batch_size", 100)

        if batched:
            assert self.stream_mongo is False, "Batched mapping is not supported in streaming mode."
            transformed = []
            for i in range(0, len(self.data), batch_size):
                batch = self.data[i:i + batch_size]
                batch_result = [func(item) for item in batch]
                transformed.extend([r for r in batch_result if r is not None])
            self.transformed_data = transformed
            return self

        elif lazy:
            self.transform = func
            return self

        else:
            transformed_data = []
            for i in range(len(self)):
                result = func(self.__getitem__(i))
                if result is not None:
                    transformed_data.append(result)
                else:
                    print(f"Skipping item at index {i} due to None result.")
            self.transformed_data = transformed_data
            return self


    def __getitem__(self, idx):
        if self.transformed_data is not None:
            return self.transformed_data[idx]
        else:
            if self.stream_mongo:
                item = self.collection.find_one({"_id": self.ids[idx]})
            else:
                item = self.data[idx]
            result = {
                "_id": str(item["_id"]),
                "doi": item.get("doi"),
                "text": item.get("abstract"),
                "date": item.get("date")
            }

            if self.transform:
                result = self.transform(result)

            return result

    def to_dict(self):
        return [self[i] for i in range(len(self))]

    def shuffle(self, seed=None):
        if seed is not None:
            random.seed(seed)
        if self.stream_mongo:
            random.shuffle(self.ids)
        else:
            random.shuffle(self.data)
        return self

    def train_test_split(self, test_size=0.2, random_state=42, use_time_series_split=False):
        if not (0 < test_size < 1):
            raise ValueError("test_size must be between 0 and 1.")
        if self.stream_mongo:
            raise NotImplementedError("train_test_split not supported in streaming mode.")

        indices = list(range(len(self)))
        if use_time_series_split:
            tscv = TimeSeriesSplit(n_splits=int(1/test_size))
            train_indices, test_indices = list(tscv.split(indices))[-1]
        else:
            train_indices, test_indices = train_test_split(indices, test_size=test_size, random_state=random_state)

        train_dataset = BioRxivDataset(
            mongo_uri=self.client.address[0],
            db_name=self.db.name,
            collection_name=self.collection.name,
            subset_query=self.subset_query,
            stream_mongo=self.stream_mongo,
            indices=train_indices
        )
        test_dataset = BioRxivDataset(
            mongo_uri=self.client.address[0],
            db_name=self.db.name,
            collection_name=self.collection.name,
            subset_query=self.subset_query,
            stream_mongo=self.stream_mongo,
            indices=test_indices
        )

        train_dataset.transform = self.transform
        test_dataset.transform = self.transform

        train_dataset.transformed_data = [self.transformed_data[i] for i in train_indices] if self.transformed_data else None
        test_dataset.transformed_data = [self.transformed_data[i] for i in test_indices] if self.transformed_data else None

        return train_dataset, test_dataset

def tokenize_with_eos(example, tokenizer, max_length=512):
    text = example.get("text", "")
    if not text:
        print(f"Skipping empty text for _id: {example.get('_id')}")
        return None

    tokens = tokenizer(
        text,
        truncation=True,
        max_length=max_length - 1,
        padding=False,
        return_tensors=None
    )

    eos_token_id = tokenizer.eos_token_id
    if eos_token_id is None:
        raise ValueError("Tokenizer does not define an EOS token.")

    input_ids = tokens["input_ids"] + [eos_token_id]
    attention_mask = tokens["attention_mask"] + [1]

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": input_ids
    }
