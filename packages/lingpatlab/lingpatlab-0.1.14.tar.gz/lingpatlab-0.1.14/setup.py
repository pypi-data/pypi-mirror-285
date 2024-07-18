# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lingpatlab',
 'lingpatlab.analyze',
 'lingpatlab.analyze.bp',
 'lingpatlab.analyze.dmo',
 'lingpatlab.analyze.dto',
 'lingpatlab.analyze.svc',
 'lingpatlab.baseblock',
 'lingpatlab.parser',
 'lingpatlab.parser.dmo',
 'lingpatlab.parser.dto',
 'lingpatlab.parser.svc',
 'lingpatlab.segmenter',
 'lingpatlab.segmenter.bp',
 'lingpatlab.segmenter.dmo',
 'lingpatlab.segmenter.svc',
 'lingpatlab.tokenizer',
 'lingpatlab.tokenizer.bp',
 'lingpatlab.tokenizer.dmo',
 'lingpatlab.tokenizer.dto',
 'lingpatlab.tokenizer.svc',
 'lingpatlab.utils',
 'lingpatlab.utils.bp',
 'lingpatlab.utils.dmo',
 'lingpatlab.utils.dto',
 'lingpatlab.utils.os',
 'lingpatlab.utils.svc']

package_data = \
{'': ['*']}

install_requires = \
['openai', 'spacy==3.7.4', 'unicodedata2']

setup_kwargs = {
    'name': 'lingpatlab',
    'version': '0.1.14',
    'description': 'Linguistic Pattern Lab using spaCy',
    'long_description': '# LingPatLab: Linguistic Pattern Laboratory\n\n## Overview\n\nLingPatLab is a robust API designed to perform advanced Natural Language Processing (NLP) tasks, utilizing the capabilities of the spaCy library. This tool is expertly crafted to convert raw textual data into structured, analyzable forms. It is ideal for developers, researchers, and linguists who require comprehensive processing capabilities, from tokenization to sophisticated text summarization.\n\n## Features\n\n- **Tokenization**: Splits raw text into individual tokens.\n- **Parsing**: Analyzes tokens to construct sentences with detailed linguistic annotations.\n- **Phrase Extraction**: Identifies and extracts significant phrases from sentences.\n- **Text Summarization**: Produces concise summaries of input text, optionally leveraging extracted phrases.\n\n## Usage\n\nTo get started with LingPatLab, you can set up the API as follows:\n\n```python\nfrom spacy_core.api import SpacyCoreAPI\n\napi = LingPatLab()\n```\n\n### Tokenization and Parsing\n\nTo tokenize and parse input text into structured sentences:\n\n```python\nparsed_sentence: Sentence = api.parse_input_text("Your input text here.")\nprint(parsed_sentence.to_string())\n```\n\n### Phrase Extraction\n\nTo extract phrases from a structured Sentences object:\n\n```python\nphrases: List[str] = api.extract_topics(parsed_sentences)\nfor phrase in phrases:\n    print(phrase)\n```\n\n### Summarization\n\nTo generate a summary of the input text:\n\n```python\nsummary: str = api.generate_summary("Your input text here.")\nprint(summary)\n```\n\n### Data Classes\n\nLingPatLab utilizes several custom data classes to structure the data throughout the NLP process:\n\n- `Sentence`: Represents a single sentence, containing a list of tokens (`SpacyResult` objects).\n- `Sentences`: Represents a collection of sentences, useful for processing paragraphs or multiple lines of text.\n- `SpacyResult`: Encapsulates the detailed analysis of a single token, including part of speech, dependency relations, and additional linguistic features.\n- `OtherInfo`: Contains additional information about a token, particularly in relation to its syntactic head.\n',
    'author': 'Craig Trim',
    'author_email': 'craigtrim@gmail.com',
    'maintainer': 'Craig Trim',
    'maintainer_email': 'craigtrim@gmail.com',
    'url': 'https://github.com/craigtrim/lingpatlab',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
