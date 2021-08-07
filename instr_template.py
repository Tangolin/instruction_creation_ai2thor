import random

MOVEAHEAD_BESIDE = {
    'Walk along the',
    'Walk beside the',
    'Walk past the',
    'Go along the',
    'Continue ahead along the',
    'Go pass the',
    'Head forward along the',
    'Go straight ahead along the',
    'Go straight ahead past the',
    'Continue past the',
    'Go straight along the',
    'Go forward past the',
    'Walk forward along the',
    'Keep going forward past the',
}

MOVEAHEAD_TOWARD_W_OBJ = {
    'Walk towards the',
    'Walk ahead until you reach the',
    'Go towards the',
    'Go forward following the',
    'Continue forward as you see the',
    'Go straight towards the',
    'Keep walking forward towards the',
    'Walk ahead following the',
    'Continue ahead towards the',
    'Keep walking as you see the',
    'Head forward to the',
    'Walk forward to the',
    'Keep going towards the'
}

MOVEAHEAD_TOWARD = {
    'Go straight',
    'Go forward',
    'Go ahead',
    'Walk forward',
    'Head straight',
    'Walk straight',
    'Walk forward',
    'Keep going forward',
}

ROTATE_W_OBJ = {
    'Turn <DIR> at the',
    'Head <DIR> when you are near the',
    'Make a <DIR> turn at the',
    'Go towards the <DIR> when you are at the',
    'Go <DIR> at the',
    'Take a <DIR> at the',
    'Go <DIR> around the',
    'Turn <DIR> before the',
    'Head <DIR> at the',
    'Turn <DIR> when you are near the',
    'Turn <DIR> when you see the'
}

ROTATE = {
    'Turn <DIR>',
    'Make a <DIR>',
    'Go <DIR>',
    'Head <DIR>'
}

STOP = {
    'Wait there.',
    'Stop there.',
    'Stop',
    'Stay there',
}

STOP_W_OBJ = {
    'Wait at the',
    'Stop in front of the',
    'Stop at the',
    'Stop beside the',
    'Stop by the',
    'Stop near the',
    'Wait beside the',  
    'Wait by the',
}

CONJUNCTIONS = {
    'and',
    'then',
    'and then'
}

forward_list = [MOVEAHEAD_TOWARD_W_OBJ, MOVEAHEAD_TOWARD]
rotate_list = [ROTATE, ROTATE_W_OBJ]

def sentence_template(no_objs):
    token = '<blank>'
    sentences = [[] for i in range(no_objs)]

    for i, sentence in enumerate(sentences):
        if i == len(sentences) - 1:
            first = random.sample(random.sample(forward_list, 1)[0], 1)[0]
            sentence.append(first)
            if first in MOVEAHEAD_TOWARD:
                sentence.append(random.sample(CONJUNCTIONS, 1)[0])
                sentence.append(random.sample(STOP_W_OBJ, 1)[0].lower())
                sentence.append(token+'.')
            else:
                sentence.append(token)
                sentence.append(random.sample(CONJUNCTIONS, 1)[0])
                sentence.append(random.sample(STOP, 1)[0].lower())
        
        else:
            first = random.sample(random.sample(forward_list, 1)[0], 1)[0]
            sentence.append(first)
            if first in MOVEAHEAD_TOWARD:
                sentence.append(random.sample(CONJUNCTIONS, 1)[0])
                sentence.append(random.sample(ROTATE_W_OBJ, 1)[0].lower())
                sentence.append(token)
            else:
                sentence.append(token)
                sentence.append(random.sample(CONJUNCTIONS, 1)[0])
                sentence.append(random.sample(ROTATE, 1)[0].lower())
            sentence.append('.')
    
    for i in range(len(sentences)):
        sentences[i] = ' '.join(sentences[i])

    return sentences