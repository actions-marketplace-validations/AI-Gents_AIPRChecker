import openai
import colorlog
import logging
import requests
import tiktoken


from .AIPRCheckerPrompts import PERSONALITY, FINAL_CLARIFICATIONS, CHECK_SECURITY, CHECK_BUGS_AND_OPTIMIZATION

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(message)s'))

logger = colorlog.getLogger('file_generator')
if not logger.hasHandlers():
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class AIPRChecker():
    """Class that generates code using OpenAI's API"""
    
    def __init__(self, api_key: str, github_token: str, repo: str, pr_number: str, model: str="gpt-4"):
        self.api_key = api_key
        self.github_token = github_token
        self.model = model
        self.repo = repo
        self.pr_number = pr_number
        self.headers = {'Authorization': f'token {self.github_token}'}
        openai.api_key = api_key
    
    def lenTokens(self,prompt, model):
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(prompt))

    def contact(self, prompt: str, p_info_msg: bool = True) -> str:
        """Function that asks the model"""

        if p_info_msg:
            logger.info(f"Asking OpenAI: {prompt[:50]}...")

        messages = [
            {"role": "system", "content": PERSONALITY},
            {"role": "system", "content": self.program_specs},
            {"role": "user", "content": prompt},
            {"role": "system", "content": FINAL_CLARIFICATIONS}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0
        )

        all_text = response["choices"][0]["message"]["content"]

        logger.info(f"Response:\n{all_text}")

        return all_text
    

    def get_gh_diff_files(self):
        # Get the changed files from the GitHub API
        response = requests.get(f'https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}/files', headers=self.headers)

        # Make sure the request was successful
        response.raise_for_status()

        return response.json()

    def analyze_patch(self, msg):
        """Function that analyzes a patch"""

        # Prepare a comment with the diffs of all changed files
        diff_files = self.get_gh_diff_files()
        for orig_msg in [CHECK_SECURITY, CHECK_BUGS_AND_OPTIMIZATION]:
            msg = orig_msg
            for diff_file in diff_files:
                new_part = f'Diff for {diff_file["filename"]}:\n```\n{diff_file["patch"]}\n```\n\n'
                if self.lenTokens(msg+new_part, self.model) > 3000:
                    answer = self.contact(msg)
                    self.post_gh_comment(answer)
                    msg = orig_msg

                msg += new_part             
        
            if msg != orig_msg:
                answer = self.contact(msg)
                self.post_gh_comment(answer)

    
    def post_gh_comment(self, comment: str):
        # Post the comment to the pull request
        comment_response = requests.post(
            f'https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments',
            headers=self.headers,
            json={'body': comment}
        )

        # Make sure the request was successful
        comment_response.raise_for_status()
