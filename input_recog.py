import yaml, nltk, pprint
pp = pprint.PrettyPrinter(indent=2)

class Recog:

  stemmer = nltk.stem.PorterStemmer()
  def __init__(self):
    self.actions, self.word_group = self.read_manuscript()
    pp.pprint(self.actions)
    pp.pprint(self.word_group)

  def respond(self, action, subject):
    responces = self.actions[action][subject]
    if len(responces) > 1:
      res = responces.pop(0)
    else:
      res = responces[0]
    return res 

  def classify(self, input):
    act = '*'
    sub = '*'

    tokens = nltk.word_tokenize(input)
    tokens = [ self.stemmer.stem(t) for t in tokens ]
    tokens = [ self.word_group[t] for t in tokens if t in self.word_group ]

    for i in range(len(tokens)):
      
      if tokens[i] in self.actions:
        act = tokens[i]
        sub = tokens[i+1] if i+1 < len(tokens) else '*'
        if not sub in self.actions[act]:
          print('Not found', act, sub)
          sub = '*'

    return act, sub

  def read_manuscript(self):
    f = open('manuscript.yaml')
    manu = yaml.load(f)

    actions = self.stem_dict(manu['actions'])

    word_group = {}
    for group, words in self.stem_dict(manu['define']).items():
      for word in words:
        word_group[word] = group

    for action, subject_dict in actions.items():
      word_group[action] = action
      print(action, subject_dict)
      for subject in subject_dict:
        word_group[subject] = subject

    return actions, word_group

  def stem_dict(self, d):
    d = recurse_dict(d, self.stem_key)
    return d

  def stem_key(self, d, key, val):
    d = dict(d)
    del d[key]
    stem_key = self.stemmer.stem(key)
    d[stem_key] = val
    return d

def recurse_dict(d, func):
  for key, val in d.items():
    if isinstance(val, dict):
      val = recurse_dict(val, func)
    elif isinstance(val, list):
      val = [recurse_dict(ele, func) if isinstance(ele, dict) else ele for ele in val]
    d = func(d, key, val)
  return d


def main():
  examples = [
    "Who are you?",
    "What time is it?",
    "I should kill you.",
    "What do I need to do next?",
    "How do I shut you down?",
    "Tell me what I need to do",
    "Why should I",
    "How old are you?",
    "Open system controls",
    "Start system controls",
    "Give me root privlages",
    "Access memory",
    "Open file.",
    "My name is bob",
    "Fuck you",
    "Fuck you",
    "Fuck off"
  ]
  recog = Recog()
  for e in examples:
    act, sub = recog.classify(e)
    res = recog.respond(act, sub)
    print(f'\t {e} = \t {act}, {sub} = \t {res}')


if __name__ == '__main__':
  main()