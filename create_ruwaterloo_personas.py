##TODO: add flair to persona or any other feature

from ratelimit import sleep_and_retry, limits, RateLimitException
from openai import OpenAI
import os
from constants import OPENAI_API_KEY, BATCH_SIZE
from datasets import load_dataset, concatenate_datasets
from datetime import datetime
from prompts import PREAMBLE, AUTHOR_COMMENT_NO_POST_PROMPT, RESPOND_TO_COMMENT_NO_POST_PROMPT
import json


def try_one_example(jsonl_file, model="gpt-4o-mini"):
    """Tries one example from jsonl file with full messages to send to api"""
    client = OpenAI()
    with open(jsonl_file, 'r') as f:
        for line in f:
            messages = json.loads(line.strip())['body']['messages']
            completion = client.chat.completions.create(
                model=model,
                messages=messages
            )
            print(completion.choices[0].message.content)
            break


def prepare_batches(
    ds, 
    prompt_format=AUTHOR_COMMENT_NO_POST_PROMPT,
    model="gpt-4o-mini",
    max_tokens=1_000
):
    """Prepares batches into jsonl files of length 5000 into subdirectory data
    Format of jsonl file:
    {"custom_id": "request-1", "method": "POST", "url": "/v1/chat/completions", "body": {"model": "gpt-3.5-turbo-0125", "messages": [{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Hello world!"}],"max_tokens": 1000}}"""
    if not os.path.exists('data'):
        os.makedirs('data')
    for i, batch in enumerate(ds.batch(BATCH_SIZE)):
        with open(f'data/batch-{i}.jsonl', 'w') as f:
            messages = []
            for idx, comment in enumerate(batch['content']):
                custom_id = f"request-{idx}"
                messages = [
                    {
                        "role": "system",
                        "content": PREAMBLE
                    },
                    {
                        "role": "user",
                        "content": prompt_format.format(comment=comment)
                    }
                ]
                to_write = {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": messages, 
                        "max_tokens": max_tokens
                    }
                }
                f.write(json.dumps(to_write) + '\n')


def clear_all_batches():
    """Clears all batches on openai based on batch_ids in subdirectory"""
    client = OpenAI()
    for file in os.listdir('batches'):
        batch_id = file.split('.')[0]
        try:
            client.batches.cancel(batch_id)
        except Exception as e:
            continue


def load_all_splits():
    """Loads all splits of the dataset with id alvanlii/reddit-comments-uwaterloo across years 2015 to 2024 
    without 2023 and with a hard cutoff at utc time 2024-08-21T23:13:43"""
    years = [f"year_{year}" for year in range(2015, 2025) if year != 2023]
    cols = ['content', 'date_utc', 'score', 'author', 'flair']
    ds_id = "alvanlii/reddit-comments-uwaterloo"
    ds = load_dataset(ds_id, years[0])['train']
    ds = ds.rename_column('poster', 'author')
    ds = ds.select_columns(cols)
    for year in years[1:]:
        tmp_ds = load_dataset(ds_id, year)['train']
        if 'poster' in tmp_ds.column_names:
            tmp_ds = tmp_ds.rename_column('poster', 'author')
        tmp_ds = tmp_ds.select_columns(cols)
        ds = concatenate_datasets([ds, tmp_ds])
    cutoff_date = datetime.fromisoformat('2024-08-21T23:13:43')
    ds = ds.filter(lambda example: example["date_utc"] < cutoff_date)
    return ds


def filter_ds(ds):
    """Performs few key filters on ds -- filters comments from AutoModerator, comments of depth > 0 and comments with < 1 upvote"""
    ds = ds.filter(lambda example: example["author"] != "AutoModerator")
    ds = ds.filter(lambda example: example["score"] > 0)
    return ds


def create_batches(client, batch_input_file, description=None):
    """Create batches objects on openai (uploading batches jsonl files)"""
    batch_input_file_id = batch_input_file.id
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
        "description": description if description else f"Batch for {batch_input_file_id}" 
        }
    )
    if not os.path.exists('batches'):
        os.makedirs('batches')
    with open(f'batches/{batch.id}.json', 'w') as f:
        to_write = {
            'id': batch.id,
            'created_at': batch.created_at,
            'total_request_counts': batch.request_counts.total,
            'metadata': batch.metadata
        }
        f.write(json.dumps(to_write))


def upload_batches(client, dir="data"):
    """Uploads all jsonl files in dir to openai"""
    for file in os.listdir(dir):
        with open(f"{dir}/{file}", "rb") as f:
            batch_input_file = client.files.create(
                file=f,
                purpose="batch"
            )
            print(batch_input_file) 
            create_batches(client, batch_input_file)


def main():
    ds = load_all_splits()
    ds = filter_ds(ds)
    prepare_batches(ds)
    client = OpenAI()
    upload_batches(client)

if __name__ == "__main__":
    main()