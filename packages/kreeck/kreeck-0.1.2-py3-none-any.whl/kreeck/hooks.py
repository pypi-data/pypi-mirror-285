import os
import subprocess

def install_hooks(repo_path='.'):
    hooks_path = os.path.join(repo_path, '.git', 'hooks')
    post_commit_path = os.path.join(hooks_path, 'post-commit')
    
    with open(post_commit_path, 'w') as hook_file:
        hook_file.write('#!/bin/sh\n')
        hook_file.write('kreeck contribute\n')
    
    subprocess.run(['chmod', '+x', post_commit_path])

def uninstall_hooks(repo_path='.'):
    hooks_path = os.path.join(repo_path, '.git', 'hooks')
    post_commit_path = os.path.join(hooks_path, 'post-commit')
    
    if os.path.exists(post_commit_path):
        os.remove(post_commit_path)
