__mf_extensions__ = "huggingface_dataset"

import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("metaflow-card-hf-dataset").version
except:
    # this happens on remote environments since the job package
    # does not have a version
    __version__ = None
