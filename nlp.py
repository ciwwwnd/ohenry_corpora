import re
import sqlite3
import pymorphy2

conn = sqlite3.connect("articles2.db", check_same_thread=False)
cursor = conn.cursor()

morph = pymorphy2.MorphAnalyzer()


def get_word_in_qoutes(query, check_word_index):
    query_word = re.sub('"', '', query).lower()
    if check_word_index == 0:
        cursor.execute('SELECT text_index, sentence_index from pos_tags where word = "'+query_word+'"')
    else:
        cursor.execute('SELECT text_index, sentence_index, word_index from pos_tags where word = "'+query_word+'"')
    return cursor.fetchall()


def get_word_with_pos(query, check_word_index):
    query_lemma = morph.parse(query.split('+')[0])[0].normal_form
    query_tag = query.split('+')[1].upper()
    if check_word_index == 0:
        cursor.execute('SELECT text_index, sentence_index from pos_tags where lemma = "'+query_lemma+'" and pos = "'+query_tag+'"')
    else:
        cursor.execute('SELECT text_index, sentence_index, word_index from pos_tags where lemma = "'+query_lemma+'" and pos = "'+query_tag+'"')
    return cursor.fetchall()


def get_pos(query, check_word_index):
    query_pos = query.upper()
    if check_word_index == 0:
        cursor.execute('SELECT text_index, sentence_index from pos_tags where pos = "'+query_pos+'"')
    else:
        cursor.execute('SELECT text_index, sentence_index, word_index from pos_tags where pos = "'+query_pos+'"')
    return cursor.fetchall()


def get_word(query, check_word_index):
    lemmatized_query = morph.parse(query.lower())[0].normal_form
    if check_word_index == 0:
        cursor.execute('SELECT text_index, sentence_index from pos_tags where lemma = "'+lemmatized_query+'"')
    else:
        cursor.execute('SELECT text_index, sentence_index, word_index from pos_tags where lemma = "'+lemmatized_query+'"')
    return cursor.fetchall()


def check_type(query, checker):
    if '"' in query:
        return get_word_in_qoutes(query, checker)

    elif len(re.findall('[A-Z]+', query)) != 0:

        if len(query.split('+')) == 2:
            return get_word_with_pos(query, checker)
        elif len(query.split('+')) == 1:
            return get_pos(query, checker)

    else:
        return get_word(query, checker)


def compare_texts(texts):
    sntncs = {}
    for i in range(1, len(texts)):
        for word in texts[0]:
            if (word[0], word[1], word[2]+i) in texts[i]:
                try:
                    sntncs[(word[0], word[1])] += 1
                except:
                    sntncs[(word[0], word[1])] = 1
    sentences = []
    for k, v in sntncs.items():
        if v == len(texts)-1:
            sentences.append(k)
    return sentences


def get_indexes(query):
    if len(query.split(' ')) == 1:
        texts = check_type(query, 0)
        return texts
    elif len(query.split(' ')) > 1:
        query_tokens = query.split(' ')
        texts_to_compare = []
        for token in query_tokens:
            texts = check_type(token, 1)
            texts_to_compare.append(texts)
        texts = compare_texts(texts_to_compare)
        return texts
    else:
        print("Запрос пустой")


def searching(query):
    texts = get_indexes(query)
    sentences = []
    titles = []
    result = []
    for text in texts:
        cursor.execute(
            'SELECT sentence from sentences where text_index = "' + str(text[0]) + '" and sentence_index = "' + str(
                text[1]) + '"')
        sentences.append(cursor.fetchall()[0][0])
        cursor.execute('SELECT title from titles where text_index = "' + str(text[0]) + '"')
        titles.append(cursor.fetchall()[0][0])
    for i in range(len(sentences)):
        result.append(sentences[i] + ' [О. Генри, ' + titles[i] + ']')
    return result