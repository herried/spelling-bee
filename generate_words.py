# -*- coding: utf-8 -*-
import os, sys
import json, glob, csv, re
from urllib2 import Request, urlopen, URLError
import urllib

# SET THESE VARIABLES
debug = False
api_key = "PASTE_YOUR_WORDNIK_API_KEY_HERE"

# LEAVE THESE ALONE
base_url = "http://api.wordnik.com:80/v4/word.json"

# HELPER METHOD FOR API CALLS
def api_get(u):
    request = Request(u)
    data = []
    try:
        response = urlopen(request)
        data = json.load(response)
    except URLError, e:
        pass
    finally:
        return data

# HELPER METHOD TO CLEAN UP THE TEXT
def clean_text(t):
    return t.replace("\n","").replace("\t","").replace("|","").strip().encode('utf-8')

# MAIN METHOD
def main():

    # Set up working directories
    working_dir = os.path.dirname(os.path.realpath(__file__))
    src_word_dir = os.path.join(working_dir,"words")
    if debug == True:
        src_word_dir = os.path.join(working_dir,"words_test")

    out_dir = os.path.join(working_dir,"output")
    out_txt_dir = os.path.join(out_dir,"lists")
    out_html_dir = os.path.join(out_dir,"html")

    if not os.path.exists(out_txt_dir):
        os.makedirs(out_txt_dir)

    if not os.path.exists(out_html_dir):
        os.makedirs(out_html_dir)

    # Check for the text files
    txt_files = glob.glob(os.path.join(src_word_dir,"*.txt"))

    if len(txt_files) < 0:
        print "ERROR: No source text files found in 'words' directory."
        sys.exit(0)

    # Loop through the source text files
    for txt_file in txt_files:
        round_name = os.path.splitext(os.path.basename(txt_file))[0]
        print "Processing Round: %s"%round_name

        # Create HTML directory
        if not os.path.isdir(os.path.join(out_html_dir,"_"+round_name)):
            os.mkdir(os.path.join(out_html_dir,"_"+round_name))

        # Start writing the reference text file
        with open(os.path.join(out_txt_dir,'%s.txt'%round_name), 'wb') as data_file:
            cw = csv.writer(data_file,
                            dialect="excel-tab",
                            delimiter="\t",
                            quoting=csv.QUOTE_ALL)

            cw.writerow(["ID","Word","Pronunciation","Definition","Etymology","Example"])

            words = []
            txt = open(txt_file,"r")
            words = txt.readlines()
            txt.close()

            wt=len(words)  # Total Word Count
            print "+Found %s words."%wt

            wc = 0 # Running Word Count
            ws = 1 # Successful Word Count
            we = [] # Error Word Count

            print "+Round Progress (words):",
            for word in words:
                if wc % 25 == 0:
                    print wc,


                word_error = False

                # Remove newlines (\n) and send lowercase
                word = word.replace("\n","").lower()

                # Remove words with that may have weird stuff
                regex = re.match("[a-z]",word)
                if regex == False:
                    word_error = True

                if word_error == False:
                    def_url = "%s/%s/definitions?limit=1&api_key=%s"%(base_url,word,api_key)
                    def_data = api_get(def_url)
                    if def_data:
                        definition = clean_text(def_data[0]['text'])
                    else:
                        definition = ""
                        word_error = True

                if word_error == False:
                    te_url = "%s/%s/topExample?api_key=%s"%(base_url,word,api_key)
                    te_data = api_get(te_url)
                    if te_data:
                        top_example = clean_text(te_data["text"])
                    else:
                        top_example = ""
                        word_error = True

                if word_error == False:
                    ety_url = "%s/%s/etymologies?limit=1&api_key=%s"%(base_url,word,api_key)
                    ety_data = api_get(ety_url)
                    if ety_data:
                        etymology = clean_text(ety_data[0])
                        etymology = etymology.replace("<?xml version=\"1.0\" encoding=\"UTF-8\"?>","")
                    else:
                        etymology = ""
                        word_error = True

                if word_error == False:
                    pro_url = "%s/%s/pronunciations?limit=1&api_key=%s"%(base_url,word,api_key)
                    pro_data = api_get(pro_url)
                    if pro_data:
                        pronunciation = clean_text(pro_data[0]["raw"])
                    else:
                        pronunciation = ""
                        word_error = True

                if word_error == False:
                    aud_url = "%s/%s/audio?limit=1&api_key=%s"%(base_url,word,api_key)
                    aud_data = api_get(aud_url)
                    if aud_data:
                        audio_url = clean_text(aud_data[0]["fileUrl"])
                        mp3_error = False
                        try:
                            mp3 = urllib.URLopener()
                            mp3_name = "%s_%s_audio.mp3"%(round_name,ws)
                            mp3_path = os.path.join(out_html_dir,"_"+round_name,mp3_name)
                            mp3.retrieve(audio_url,mp3_path)
                        except Exception as e:
                            mp3_error = True
                    else:
                        audio_url = ""
                        word_error = True

                if word_error == False:
                    # Write CSV
                    cw.writerow([wc,word,pronunciation,definition,etymology,top_example])

                    # Write HTML
                    # Blank Template
                    bt = open(os.path.join(working_dir,"output","tpl","_blank.html"), "r")
                    btt = str(bt.read())
                    bt.close()

                    btt = btt.replace("PREVWORDPAGE","%s_%s_word"%(round_name,ws-1))
                    btt = btt.replace("NEXTWORDPAGE","%s_%s_word"%(round_name,ws))
                    if mp3_error:
                        btt = btt.replace("id=\"mp3_button\"","id=\"mp3_button\" style=\"display:none;\"")
                    else:
                        btt = btt.replace("WORDMP3FILE","%s_%s_audio.mp3"%(round_name,ws))


                    bp = open(os.path.join(out_html_dir,"_"+round_name,"%s_%s_blank.html"%(round_name,ws)),"w")
                    bp.write(btt)
                    bp.close()

                    # Word Template
                    wt = open(os.path.join(working_dir,"output","tpl","_word.html"), "r")
                    wtt = str(wt.read())
                    wt.close()

                    wtt = wtt.replace("PREVBLANKPAGE","%s_%s_blank"%(round_name,ws))
                    wtt = wtt.replace("NEXTBLANKPAGE","%s_%s_blank"%(round_name,ws+1))
                    wtt = wtt.replace("NEXTWORDSTRING",word)

                    wp = open(os.path.join(out_html_dir,"_"+round_name,"%s_%s_word.html"%(round_name,ws)),"w")
                    wp.write(wtt)
                    wp.close()

                    if wc+1 == wt:
                        print wt

                    # Add to successful words
                    ws+=1
                else:
                    we.append(word)

                # Next
                wc+=1

            print ""
            print "+Successful Words: %s"%(ws-1)
            print "+Error Words: %s"%len(we)
            if debug == True:
                if len(we)>0:
                    for w in we:
                        print w,
                    print ""
            print "+=======================+\n"

if __name__ == "__main__":
    main()
