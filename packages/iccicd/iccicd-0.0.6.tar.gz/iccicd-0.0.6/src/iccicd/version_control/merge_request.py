class MergeRequest:
    def __init__(self) -> None:
        self.source_branch = ""
        self.target_branch = ""
        self.title = ""
        self.description = ""
        self.remove_source_branch = False
        self.squash_on_merge = False
