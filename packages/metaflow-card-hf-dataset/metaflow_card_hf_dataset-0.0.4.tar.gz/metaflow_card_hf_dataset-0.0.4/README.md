## Installation

```bash
pip install metaflow-card-hf-dataset
```

## Usage

After installing the module, you can add any HuggingFace dataset to your Metaflow tasks by using the `@huggingface_dataset` decorator. This decorator has a `id` field, which is the dataset ID from HuggingFace.

```python
from metaflow import FlowSpec, step, huggingface_dataset

class Flow(FlowSpec):

    @huggingface_dataset(id="princeton-nlp/SWE-bench")
    @step
    def start(self):
        self.next(self.end)

    @huggingface_dataset(id="argilla/databricks-dolly-15k-curated-en")
    @step
    def end(self):
        pass

if __name__ == '__main__':
    Flow()
```
