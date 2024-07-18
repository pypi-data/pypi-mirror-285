Dictionary API
============

Dictionary is a simple tool for getting word definitions. It returns the definition a word.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [Dictionary API](https://apiverve.com/marketplace/api/dictionary)

---

## Installation
	pip install apiverve-dictionary

---

## Configuration

Before using the dictionary API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The Dictionary API documentation is found here: [https://docs.apiverve.com/api/dictionary](https://docs.apiverve.com/api/dictionary).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_dictionary.apiClient import DictionaryAPIClient

# Initialize the client with your APIVerve API key
api = DictionaryAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "word": "apple" }
```

###### Simple Request

```
# Make a request to the API
result = api.execute(query)

# Print the result
print(result)
```

###### Example Response

```
{
  "status": "ok",
  "error": null,
  "data": {
    "word": "apple",
    "definitionCount": 5,
    "definitions": [
      "The fleshy pome or fruit of a rosaceous tree (Pyrus malus) cultivated in numberless varieties in the temperate zones. Note: The European crab apple is supposed to be the original kind, from which all others have sprung.",
      "(bot.)  Any tree genus Pyrus which has the stalk sunken into the base of the fruit; an apple tree.",
      "Any fruit or other vegetable production resembling, or supposed to resemble, the apple; as, apple of love, or love apple (a tomato), balsam apple, egg apple, oak apple.",
      "Anything round like an apple; as, an apple of gold. Note: Apple is used either adjectively or in combination; as, apple paper or apple-paper, apple-shaped, apple blossom, apple dumpling, apple pudding. Apple blight, an aphid which injures apple trees. See Blight, n. -- Apple borer (Zoöl.), a coleopterous insect (Saperda candida or bivittata), the larva of which bores into the trunk of the apple tree and pear tree. -- Apple brandy, brandy made from apples. -- Apple butter, a sauce made of apples stewed down in cider. Bartlett. -- Apple corer, an instrument for removing the cores from apples. -- Apple fly (Zoöl.), any dipterous insect, the larva of which burrows in apples. Apple flies belong to the genera Drosophila and Trypeta. -- Apple midge (Zoöl.) a small dipterous insect (Sciara mali), the larva of which bores in apples. -- Apple of the eye, the pupil. -- Apple of discord, a subject of contention and envy, so called from the mythological golden apple, inscribed \"For the fairest,\" which was thrown into an assembly of the gods by Eris, the goddess of discord. It was contended for by Juno, Minerva, and Venus, and was adjudged to the latter. -- Apple of love, or Love apple, the tomato (Lycopersicum esculentum). -- Apple of Peru, a large coarse herb (Nicandra physaloides) bearing pale blue flowers, and a bladderlike fruit inclosing a dry berry. -- Apples of Sodom, a fruit described by ancient writers as externally of air appearance but dissolving into smoke and ashes plucked; Dead Sea apples. The name is often given to the fruit of Solanum Sodomæum, a prickly shrub with fruit not unlike a small yellow tomato. -- Apple sauce, stewed apples. [U. S.] -- Apple snail or Apple shell (Zoöl.), a fresh-water, operculated, spiral shell of the genus Ampullaria. -- Apple tart, a tart containing apples. -- Apple tree, a tree naturally bears apples. See Apple,",
      "-- Apple wine, cider. -- Apple worm (Zoöl.), the larva of a small moth (Carpocapsa pomonella) which burrows in the interior of apples. See Codling moth. -- Dead Sea Apple. (a) pl. Apples of Sodom. Also Fig. \"To seek the Dead Sea apples of politics.\" S. B. Griffin. (b) A kind of gallnut coming from Arabia. See Gallnut.  To grow like an apple; to bear apples. Holland."
    ]
  }
}
```

---

## Customer Support

Need any assistance? [Get in touch with Customer Support](https://apiverve.com/contact).

---

## Updates
Stay up to date by following [@apiverveHQ](https://twitter.com/apiverveHQ) on Twitter.

---

## Legal

All usage of the APIVerve website, API, and services is subject to the [APIVerve Terms of Service](https://apiverve.com/terms) and all legal documents and agreements.

---

## License
Licensed under the The MIT License (MIT)

Copyright (&copy;) 2024 APIVerve, and Evlar LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.