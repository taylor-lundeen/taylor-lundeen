from bs4 import BeautifulSoup
import requests
import os

# This variable sets which term to find a wikipedia page for
search_term = 'Tacoma'
# This variable sets the language to get the wikipedia page for
language_code = 'en'
# This variable sets the local directory to add the article or articles to
output_dir = r'C:\Users\Taylor\Documents\Coding_Projects\Wiki_Output'

def check_encodings(text_string):

    # This function iterates though each word in a string have iso-8859-1 encodings rather than ascii
    # and returning the indexes of the words that have iso-8859-1 encodings

    has_iso = False
    i = 0
    iso_indeces = []
    words = text_string.split()
    for word in words:
        for element in word:
            if ord(element) in range(129, 255):
                has_iso = True
                iso_indeces.append(i)
        i += 1

    return has_iso, iso_indeces

def get_wiki_text(page_body, article_name, output_dir):

    # This function scrapes the body of the webpage and adds the content into a text file within the specified directory

    title_element = page_body.find(['h1'], id="firstHeading")
    page_title = title_element.string
    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents

    text_filepath = os.path.join(output_dir, article_name + '_Wikipedia_Article')
    wiki_textfile = open(text_filepath, mode="w")
    wiki_textfile.write('Source: en.wikipedia.org\n\n')
    wiki_textfile.write(page_title)
    wiki_textfile.close()

    for pc in page_content[1:]:
        ascii_writer = open(text_filepath, mode="a", encoding="ascii")
        iso_writer = open(text_filepath, mode="a", encoding="iso-8859-1")
        utf_writer = open(text_filepath, mode="a", encoding="utf-8")

        # This portion goes through the content of the p (paragraph) elements and writes the content to the text file

        if pc.name == 'p':
            paragraph_text = ''
            p_list = pc.contents
            for p_el in p_list:
                paragraph_line = p_el.string
                if p_el.name == 'span' or p_el.name == 'sup':
                    continue
                else:
                    if paragraph_line is not None:
                        has_iso, iso_indeces = check_encodings(paragraph_line)
                        if has_iso == True:
                            i = 0
                            line_words = paragraph_line.split()
                            for word in line_words:
                                spaced_word = word + ' '
                                if i not in iso_indeces:
                                    try:
                                        ascii_writer.write(spaced_word)
                                    except Exception:
                                        try:
                                            utf_writer.write(spaced_word)
                                        except Exception as e:
                                            print(e)
                                else:
                                    try:
                                        iso_writer.write(spaced_word)
                                    except Exception:
                                        try:
                                            utf_writer.write(spaced_word)
                                        except Exception as e:
                                            print(e)
                                i += 1
                        else:
                            paragraph_text += paragraph_line

            if paragraph_text:
                try:
                    ascii_writer.write(paragraph_text)
                except Exception:
                    paragraph_words = paragraph_text.split()
                    for word in paragraph_words:
                        spaced_word = word + ' '
                        try:
                            ascii_writer.write(spaced_word)
                        except Exception:
                            try:
                                iso_writer.write(spaced_word)
                            except Exception:
                                try:
                                    utf_writer.write(paragraph_text)
                                except Exception as e:
                                    print(e)

        # This portion goes through the content of the header elements and writes the content to the text file

        elif pc.name in ['h2', 'h3', 'h4']:
            header_el = pc.contents
            header_string = header_el[0].string
            if header_string is not None:
                try:
                    ascii_writer.write('\n\n')
                    ascii_writer.write(header_el[0].string)
                    ascii_writer.write('\n\n')
                except Exception as e:
                    print(e)

        else:
            continue
        ascii_writer.close()
        iso_writer.close()
        utf_writer.close()

def get_articles_list(page_body, language_code, output_dir):

    # This function finds the url name for the top 5 search results in cases where the specified url returned multiple results

    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents
    i = 0
    for pc in page_content[1:]:
        if pc.name == 'ul':
            for x in pc.contents:
                if x.name == 'li':
                    for y in x.contents:
                        if i >= 5:
                            break
                        else:
                            if y.name == 'a':
                                article_url = y['href']
                                article_name = article_url.replace('/wiki/', '')
                                try:
                                    get_response(search_term=article_name, language_code=language_code, output_dir=output_dir, checked=True)
                                except Exception as e:
                                    print(e)
                                i += 1
                            else:
                                continue
                else:
                    continue
        else:
            continue

def check_for_multi_articles(page_body, language_code, article_name, output_dir):

    # This function checks to see whether the specified url returned multiple results or just one article

    content_element = page_body.find(['div'], class_="mw-parser-output")
    page_content = content_element.contents
    for pc in page_content[1:]:
        multi_articles = False
        if pc.name == 'div' and language_code == 'pt' and pc.has_attr('id'):
            if pc['id'] == 'disambig':
                global pt_multi_articles
                pt_multi_articles = True
        if pc.name == 'div' and language_code == 'fr' and pc.has_attr('id'):
            if pc['id'] == 'homonymie':
                global fr_multi_articles
                fr_multi_articles = True
        if pc.name == 'table' and language_code == 'it' and pc.has_attr('class'):
            for cl in pc['class']:
                if cl == 'avviso-disambigua':
                    get_articles_list(page_body, language_code, output_dir)

        if pc.name == 'p':
            p_list = pc.contents
            multi_articles_statements = [" may refer to:\n", " most often refers to:\n", " commonly refers to:\n", " most commonly refers to:\n"]
            fl_multi_articles_vars = ['fr_multi_articles', 'pt_multi_articles']
            for p_el in p_list:
                if p_el.string in multi_articles_statements and language_code == 'en':
                    multi_articles = True
            for fmav in fl_multi_articles_vars:
                if fmav in globals():
                    multi_articles = True
            if multi_articles == True:
                get_articles_list(page_body, language_code, output_dir)
            else:
                get_wiki_text(page_body, article_name, output_dir)
            break


def get_response(search_term, language_code, output_dir, checked):

    # This function sends a get request to the wikipedia url for the given search term to check the reponse

    article_name = search_term.replace(' ', '_')
    https_heading = 'https://'
    wiki_url = '.wikipedia.org/wiki/'
    wiki_full_url = https_heading + language_code + wiki_url + article_name
    response = requests.get(wiki_full_url)
    if response.status_code == 200 and checked == False:
        wiki_page = BeautifulSoup(response.text, 'html.parser')
        page_body = wiki_page.body
        check_for_multi_articles(page_body, language_code, article_name, output_dir)
    elif response.status_code == 200 and checked == True:
        wiki_page = BeautifulSoup(response.text, 'html.parser')
        page_body = wiki_page.body
        get_wiki_text(page_body, article_name, output_dir)
    elif response.status_code == 404:
        print('Error: an article with this name in this language was not found')
    else:
        print('Error')

get_response(search_term=search_term, language_code=language_code, output_dir=output_dir, checked=False)












