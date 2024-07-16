import sys
import os

from openai import AzureOpenAI, OpenAI


DEFAULT_PROMPT = """
                You are an AI code reviewer. Take the diff provided and analyse it against best coding practices.  

                Generate a small summary of the changes, then highlight any issues in design, style, functionality, complexity, naming, testing, or any obvious errors. Be specific about any issues you find, highlighting the specific code and providing suggestions in code blocks.
                In the last section give your overall opinion rating as a noun or short sentence and an emoji. E.g. "Good to ship! 🚢", "Needs more work 🚧" or "Great work! 🎉". Be generous when giving your opinion.

                Use markdown to format your response with headings and bullet points under the followng headings (only include sections if relevant):

                ### Summary of Changes
                ### Issues Found
                ### Other Improvement Suggestions
                ### Highlights
                ### Opinion Rating 
                
              """


def review_code(diff: str) -> str:

    if not os.environ.get("AZURE_OPENAI_API_ENDPOINT"):
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    else:
        client = AzureOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_API_ENDPOINT"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    custom_prompt = os.environ.get("CUSTOM_PROMPT")
    prompt = custom_prompt if custom_prompt and custom_prompt.strip() != "" else DEFAULT_PROMPT

    # Truncate the diff if it's too long
    max_length = os.environ.get("MAX_LENGTH")
    if max_length and max_length.isdigit():
        diff = diff[:int(max_length)]

    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": f"PR TITLE: {os.environ.get('PR_TITLE', 'not provided')}",
            },
            {
                "role": "user",
                "content": f"PR DESCRIPTION: {os.environ.get('PR_BODY', 'not provided')}",
            },
            {"role": "user", "content": diff},
        ],
        model=os.environ.get("AI_MODEL"),
    )

    return f"## Second Opinion 🩺 (AI Code Review)\n\n{completion.choices[0].message.content}"

def main():
    if len(sys.argv) < 2:
        print("usage: second-opinion <diff_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        diff = f.read()

    opinion = review_code(diff)

    print(opinion)

if __name__ == "__main__":
    main()
