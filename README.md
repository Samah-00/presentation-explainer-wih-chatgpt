# The GPT-Explainer Project

## Introduction

Learning Software Development is hard. Especially when you can't understand the lecturer's presentations. Wouldn't it be nice to have someone explain them for you?

You are going to implement a Python script that explains Powerpoint presentations using the GPT-3.5 AI model. The script will take as input a presentation file, send the text from each slide to GPT, and save the results together in an output file.

Cool, right?

## Requirements

### Flow of Operation

Your script should do the following:

1. Take the path of a `.pptx` file.
2. [Parse the presentation](#parsing-powerpoint-files) to get its data.
3. Go through every slide separately, and:
    1. Extract all the text from all text boxes.
    2. Insert the text into an appropriate prompt for GPT.
    3. Send the prompt in a request to the [OpenAI API](#integration-with-openai).
    4. Extract the AI's reply from the response.
4. Gather the explanations for all the slides in a list.
5. Save the list in a JSON file.

### Asynchronous Execution

It takes time for the GPT models to generate responses. If we send the slides one after another, we will have to wait for a very long time. Therefore, we will make asynchronous API calls, so that all the slides are processed at the same time.

Use Python's `async/await` syntax, together with the builtin `asyncio` package.

> Tip: [Here](https://realpython.com/async-io-python/) is an awesome guide.

### Extra Specifications

-   Your code should ignore slides without text.
-   Your code should handle weird whitespaces within presentation text.
-   The name of the output file should be the same as the original presentation (but with a `.json` suffix).

### Bonus Requirements

-   Add a timeout to the requests you make to the OpenAI API.
-   Add a convenient CLI interface for your script (use [`argparse`](https://docs.python.org/3/library/argparse.html)).
-   Handle errors raised while processing a slide. Instead of allowing the entire program to crash, save the explanations for the other slides as usual, and put an informative error message for the slide that failed.

> Tip: [Here](https://platform.openai.com/docs/guides/error-codes/python-library-error-types) is a list of potential errors you might encounter.

## Parsing Powerpoint Files

There are several Python packages that can help you parse `.pptx` files and extract their data.

We recommend installing the [`python-pptx`](https://pypi.org/project/python-pptx/) package.

> Tip: The documentation of `python-pptx` is a bit annoying. Concentrate on the parts that are relevant for what you need.

## Integration with OpenAI

### Making API Calls

To send requests you will need to create an OpenAI account on the [OpenAI website](https://platform.openai.com/overview). There is a "Sign up" button on the top-right.

You will then need to [generate an API key](https://platform.openai.com/account/api-keys), that will be your identifier when using the API.

Also, instead of sending HTTP requests directly, it is much easier to use the official [`openai`](https://pypi.org/project/openai/) Python package to do that for you.

> Tip: Here is a [good guide](https://medium.com/geekculture/a-simple-guide-to-chatgpt-api-with-python-c147985ae28) that covers everything.

### Choosing an AI Model

OpenAI is a company that develops [AI models](https://platform.openai.com/docs/models/overview). Each model specializes in something different. For this project, it is best to use the `gpt-3.5-turbo` model (it's also the model used by the ChatGPT website).

### Writing a Good Prompt

You should think carefully how to ask GPT in a way that will give you the best answers. You cannot just throw some text from a presentation and expect it to know what you want. Here are a few good questions to ask yourself when designing a prompt:

-   How can I clearly explain what I want the AI to do for me?
-   Which information is relevant besides the text of the slide?
-   Is there any additional background that might be useful for the AI to know?

> Tip: You can easily test your prompts on [ChatGPT](https://chat.openai.com/).

### Limits

When you create a new OpenAI account you will be able to use the API for free for 3 weeks, or until you use a certain amount of [tokens](https://platform.openai.com/docs/introduction/tokens). After that you must pay. You can check how much you've spent on your [account page](https://platform.openai.com/account/usage).

Don't worry! You should have enough free tokens so you don't have to pay during this project. After 3 weeks you can create a new account with a different email (and phone number), and generate a new API key.

Also, free users have a [rate limit](https://platform.openai.com/account/rate-limits) of 3 requests per minute. If you try to send 20 requests at the same time, don't be surprised if you get errors...

## Grading

Your work will be graded based on the following criteria:

-   The code passes all mandatory [requirements](#technical-requirements).
-   Code quality
    -   Readable code
    -   Indicative names
    -   Spacing and indentation
    -   Avioding duplicate code
    -   Comments and documentation
    -   Proper division of logic into small functions
    -   Proper division of modules into separate files
-   Proper usage of Git
    -   Small and standalone commits
    -   Descriptive commit messages
    -   Working on different features in separate branches
    -   Creating a proper pull request
    -   Not uploading junk files that are not part of the code (use `.gitignore`)
-   [Bonus requirements](#bonus-requirements) you may have implemented

> Tip: Here are some [guidelines](https://gist.github.com/luismts/495d982e8c5b1a0ced4a57cf3d93cf60) on good commit practices.

## Some Extra Tips

-   Before you write code:
    -   Make sure you have a vision for the flow and architecture of your project.
    -   Play a bit with the different packages. Not too much. Just to feel comfortable.
    -   Ask yourself the following:
        -   Which logical parts does my project have?
        -   Which files should I have?
        -   Which functions should I write?
        -   Which branches should I open?
        -   Which parts of code will depend on others? Which won't?
        -   Which features are central? Which are less important?
-   Good questions to ask while coding:
    -   Do these changes really belong in the same commit?
    -   Can I give a name to this piece of logic and make a separate function?
    -   Do I really have to fix this issue right now?
    -   Is this really worth the time I'm investing?
    -   If I want to add extra features later, will it be easy?
    -   If someone else looks at this code, will they hate me?
    -   Will I understand this commit message in a week from now?
-   Before you submit:
    -   Code-review yourself! It's a good practice.

## Good Luck!

![Hunger Games](https://img.memegenerator.net/instances/47706789.jpg)
