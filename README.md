# Spider to check embedded code

## Requiremant
- python 3.6+

## Initial
- pip install -r requirements.txt
- add black list FQDM in config/blacl_list if needed

## Start to use
- python main.py -k keyword -u url -d domain
- python main -e true/false

## Result
- ./dist/result, e.g. http://xxxxxx False
- ./dist/error.log, error log
- ./dist/extract_xxx, extract True/False urls from result

## Parameters
- "-u", url to start
- "-b", black list path
- "-k", keyword
- "-e", extract result
- "-t", delay time
- "-d", domain
