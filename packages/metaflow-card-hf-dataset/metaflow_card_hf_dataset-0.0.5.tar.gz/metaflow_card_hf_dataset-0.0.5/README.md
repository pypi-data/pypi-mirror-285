## Installation

```bash
pip install metaflow-card-hf-dataset
```

## Usage

After installing the module, you can add any HuggingFace dataset to your Metaflow tasks by using the `@huggingface_dataset` decorator. There are two ways to use the decorator:
    - Via the `id` argument, which is the dataset ID from HuggingFace.
    - Via the `artifact_id` argument, which is the name of a FlowSpec artifact that contains the dataset ID.

Use the first if your workflow always reads from the same HuggingFace dataset ID. 
Use the second if your workflow pass in dataset IDs as parameters or changes them dynamically.

```python
from metaflow import FlowSpec, step, huggingface_dataset, Parameter

class Flow(FlowSpec):

    eval_ds = Parameter('eval_ds', default='argilla/databricks-dolly-15k-curated-en', help='HuggingFace dataset id.')
    # Dynamically input: python flow.py run --eval_ds lighteval/mmlu

    @huggingface_dataset(id="princeton-nlp/SWE-bench")
    @step
    def start(self):
        self.another_one = 'wikimedia/wikipedia'
        self.next(self.end)

    @huggingface_dataset(artifact_id="another_one") # Use the dataset ID set to an artifact var.
    @huggingface_dataset(artifact_id="eval_ds") # Use the dataset ID passed as a parameter.
    @step
    def end(self):
        pass

if __name__ == '__main__':
    Flow()
```
