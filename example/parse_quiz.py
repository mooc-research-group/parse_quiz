# -*- coding: cp1252 -*-

#    Copyright (C) 2013  Eric Koo <erickoo@umich.edu>
#    USE Lab, Digital Media Commons, University of Michigan Library
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see [http://www.gnu.org/licenses/].

import glob
import csv
import re
from bs4 import BeautifulSoup

class FileSet:
  '''('quiz_id', 'xml_file', 'responses_file', 'output_file')'''
  def __init__(self, row):
    self.quiz_id = row[0]
    self.xml_file = row[1]
    self.responses_file = row[2]
    self.output_file = row[3]
  def __repr__(self):
    return repr((self.quiz_id, self.xml_file, self.responses_file, self.output_file))

def get_index(value, array):
  length = len(array)
  for i in range(0,length):
    if array[i]==value:
      return i

def fix_text(string):
  string = string.strip()
  string = string.replace('\xe2\x80\x9c','"')   # Replace open quotation mark
  string = string.replace('\xe2\x80\x9d','"')   # Replace close quotation mark
  string = string.replace('\xe2\x80\x93','-')   # Replace minus symbol
  string = string.replace('#','')               # Remove # symbol because incompatible with R
  return string

print 'Parsing quiz...'
print ''

quiz_id = 0
xml_file = 'Quiz XML.txt'                  # <-- Specify XML file here
txt_file = 'Detailed Quiz Responses.txt'   # <-- Specify Detailed Quiz Responses file here
output_file = 'Parsed Quiz Results.csv'    # <-- Specify output filename here
files = []
files.append(FileSet([quiz_id, xml_file, txt_file, output_file]))

for f in files:
  XML_header = []
  XML_header_extended = []
  XML_questions = []
  XML_questions_extended = []
  XML_question_types = []
  XML_question_types_extended = []
  
  # Parse "XML Quiz Questions [*].txt" to get questions and question_types
  print '   Parsing XML...'
  filename = f.xml_file
  print '   Reading file: '+filename
  with open(filename,'rU') as IN:
    soup = BeautifulSoup(IN)
  all_questions = soup.question_groups.find_all('question')
  for question_iter, q in enumerate(all_questions):
    num = 'Q'+str(question_iter+1)
    question = str(q.find('text').string.encode('utf-8')).replace('\n','').strip()
    XML_header.append(num)
    XML_questions.append(question)

    # Get question_type
    if q.find('choice_type'):
      question_type = str(q.find('choice_type').string)
    else:
      question_type = q['type']
      if question_type == 'GS_Short_Answer_Question_Simple_With_Hidden_Field':
        if re.search(r'function setup_matrix_question',question):
          question_type = 'grid'
        else:
          question_type = 'text'
      else:
        question_type = 'text'
    XML_question_types.append(question_type)
    
    if question_type=='checkbox':
      # Checkbox question: create a separate column for each question option
      options = q.find('option_group').find_all('option')
      for index, option in enumerate(options):
        option_str = str(option.find('text').string).replace('\n',' ').strip()
        XML_header_extended.append(num+'_'+str(index+1))
        XML_questions_extended.append(question+'-'+option_str)
        XML_question_types_extended.append(question_type)
    elif question_type == 'grid':
      # Matrix question: create a separate column for each question
      matrix_re = re.search(r'.*<script>.*setup_matrix_question\(.*\[(.*)\],.*\[.*\].*</script>(.*)',question)
      matrix_main = matrix_re.group(2).strip()
      matrix_list = matrix_re.group(1).strip()
      matrix_list = matrix_list.split(',')
      for index, item in enumerate(matrix_list):
        if re.search(r'\'(.*)\'',item):
          matrix_list[index] = matrix_main + '-' + re.search(r'\'(.*)\'',item).group(1)
          matrix_list[index] = fix_text(matrix_list[index])
      for index, item in enumerate(matrix_list):
        if item != '':
          XML_questions_extended.append(item)
          XML_header_extended.append(num+'_'+str(index+1))
          XML_question_types_extended.append(question_type)
    else:
      # Normal question: use a single column
      XML_header_extended.append(num)
      XML_questions_extended.append(question)
      XML_question_types_extended.append(question_type)

  print '   Done. ('+str(question_iter+1)+' questions)'
  print ''

  # Parse "Detailed Quiz Responses [*].txt" to get responses
  print '   Parsing responses...'
  filename = f.responses_file
  print '   Reading file: '+filename
  with open(filename,'rU') as IN:
    header = ['V1','V2'] + XML_header_extended
    questions = []
    for i, question in enumerate(XML_questions_extended):
      questions.append('['+XML_question_types_extended[i]+'] ' + question)
    questions = ['user_id','name'] + questions
    responses = []

    current_question = 1
    response_num = 0
    for row in IN:
      row = row.strip()
      if row == 'Questions':
        input_type = 'questions'
        IN.next()
      elif row == 'Student Answers':
        input_type = 'student_responses'
        IN.next()
        IN.next()

      if input_type=='questions' and row!='Questions' and row!='':
        # Skip over questions because we already have these from the XML file
        num, question = row.split('\t')
        #header.append(num)
        #questions.append(question)
      elif input_type =='student_responses' and row!='Student Answers':
        if row=='':
          # End of student response: append results and reset question counter 
          responses.append(current_row)
          current_question = 1
          response_num += 1
        else:
          content = row.split('\t')
          if len(content)==2:
            # Start of student response: initialize row for new student
            user_id = content[0][1:-1]
            name = content[1]
            current_row = [user_id,name]
            for i in range(0,len(XML_header_extended)):
              if (XML_question_types_extended[i] == 'checkbox'):
                current_row.append('FALSE')
              else:
                current_row.append(None)
            current_question = 1
          else:
            # Record student responses: populate row entries
            num = 'Q' + str(int(content[0].replace('-','').replace('Q',''))+1)
            current_question = int(num.replace('Q',''))-1
            if num in XML_header:
              if XML_question_types[current_question]=='checkbox':
                # Checkbox question: find which columns to record responses
                if get_index(XML_questions[current_question]+'-'+content[3],questions):
                  current_row[get_index(XML_questions[current_question]+'-'+content[3],questions)] = 'TRUE'
              elif XML_question_types[current_question]=='grid':
                # Matrix question: add responses to separate columns
                if len(content)==4:
                  response_list = content[3][:-1].split('|')
                  for index, response in enumerate(response_list):
                    if response == 'undefined':
                      current_row[get_index(num+'_'+str(index+1),header)] = None
                    else:
                      current_row[get_index(num+'_'+str(index+1),header)] = fix_text(response)
              else:
                # Normal question: record response
                if len(content)==4:
                  default_re = re.match(r'please select', content[3].lower())
                  if not default_re:
                    current_row[get_index(num,header)] = fix_text(content[3])

    # Append last entry
    responses.append(current_row)
    response_num += 1
    
  print '   Done. ('+str(response_num)+' responses)'
  print ''
  
  # Output to formatted .csv file
  filename = f.output_file
  print '   Writing to file: '+filename
  print '   Processing...'
  with open(filename,'wb') as OUT:
    writer = csv.writer(OUT,delimiter=',')
    writer.writerow(header)
    writer.writerow(questions)
    for response in responses:
      writer.writerow(response)
  print '   Done.'
  print ''

print 'Parsing complete.'
print ''
print ''
close = raw_input('Press any key to close this window.')
