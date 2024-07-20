# yuseful_prompts

## pre requisites

- `ollama` installed with `llama3` downloaded

## test

- `python3 -m pytest -v ./yuseful_prompts/test_useful_prompts.py`

### snapshot of LLMs performance during tests

Here are the results on running the tests on a Intel® Xeon® Gold 5412U server with 256 GB DDR5 ECC and no GPU.

#### financial headlines sentiment extraction

| Model              | Status | Time (s) |
|--------------------|--------|----------|
| llama3             | OK     | 17.68    |
| phi3               | OK     | 17.84    |
| aya                | OK     | 21.68    |
| mistral            | OK     | 21.76    |
| mistral-openorca   | OK     | 22.20    |
| gemma2             | OK     | 23.14    |
| phi3:medium-128k   | OK     | 45.87    |
| phi3:14b           | OK     | 47.36    |
| aya:35b            | OK     | 77.99    |
| llama3:70b         | OK     | 144.62   |
| qwen2:72b          | OK     | 148.25   |
| command-r-plus     | OK     | 239.20   |
| qwen2              | OKKO   | 16.11    |

I've set `qwen2` to `OKKO` as it systemtically considers that `Hedge funds cut stakes in Magnificent Seven to invest in broader AI boom` is a `very bullish`, I didn't discard the model entirely since this is open to interpretation...
