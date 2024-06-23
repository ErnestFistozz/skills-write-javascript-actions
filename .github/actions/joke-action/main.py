import git
from git import Repo
import os

def get_submodule_commits(submodule_path, start_commit, end_commit):
    commits = []
    repo = git.Repo(submodule_path)
    for commit in repo.iter_commits(rev=f'{start_commit}..{end_commit}'):
        commits.append(commit)
    return commits

def print_commit_details(commits):
    for commit in commits:
        print(f"Commit Hash: {commit.hexsha}")
        print(f"Message: {commit.message.strip()}")
        print(f"Author: {commit.author}")
        print(f"Timestamp: {commit.committed_datetime}")
        print(f"Files Changed: {len(commit.stats.files)}")
        print(f"File Names: {list(commit.stats.files.keys())}")
        print("-" * 40)

def find_commit_changing_foundation(repo, file_path, new_value):
    prev_value = None
    for commit in repo.iter_commits(paths=file_path):
        file_contents = (commit.tree / file_path).data_stream.read().decode('utf-8')
        foundation_line = next(line for line in file_contents.splitlines() if 'foundation =' in line)
        foundation_value = foundation_line.split('=')[1].strip()
        if foundation_value == new_value:
            if prev_value is not None and prev_value != new_value:
                return commit
        prev_value = foundation_value
    return None

# Define paths
parent_repo_path = 'path_to_parent_repo'  # Update this with the path to your parent repo
submodule_b_path = os.path.join(parent_repo_path, 'submodB')
product_info_path = '.product-info'

# Initialize the parent repo
parent_repo = Repo(parent_repo_path)

# Get latest and second latest commits in the parent repo
latest_commit = parent_repo.commit('HEAD')
second_latest_commit = parent_repo.commit('HEAD~1')

# Get submodule B commits between the latest and second latest commits in the parent repo
submod_commits = get_submodule_commits(submodule_b_path, second_latest_commit.hexsha, latest_commit.hexsha)

# Print submodule B commit details
print("Submodule B commits between the latest and second latest commits in the parent repo:")
print_commit_details(submod_commits)

# Get the latest value of foundation from the .product-info file
latest_product_info_contents = (latest_commit.tree / product_info_path).data_stream.read().decode('utf-8')
latest_foundation_value = next(line for line in latest_product_info_contents.splitlines() if 'foundation =' in line).split('=')[1].strip()

# Find the commit that changed the foundation value to the latest value
commit_changing_foundation = find_commit_changing_foundation(parent_repo, product_info_path, latest_foundation_value)

if commit_changing_foundation:
    # Get submodule B commits between the latest commit and the commit that changed the foundation value
    submod_commits_since_change = get_submodule_commits(submodule_b_path, commit_changing_foundation.hexsha, latest_commit.hexsha)

    # Print submodule B commit details
    print("Submodule B commits between the latest parent commit and the commit changing the foundation value:")
    print_commit_details(submod_commits_since_change)
else:
    print("No commit found changing the foundation value to the latest value.")
