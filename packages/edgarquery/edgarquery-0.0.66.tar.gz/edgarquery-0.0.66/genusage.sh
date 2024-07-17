#! /bin/sh
#set -ex


D=src/edgarquery

for i in edgarcikperson.py \
    edgarcompanyconcepttocsv.py \
    edgarcompanyfactsshow.py \
    edgarcompanyfactstocsv.py \
    edgarcompanyfactsziptocsv.py \
    edgarlatest10K.py \
    edgarlatestsubmission.py \
    edgarlatestsubmissions.py \
    edgarquery.py \
    edgarsubmissions.py \
    edgarsubmissionsziptocsv.py \
    edgartickerstocsv.py \
    edgarxbrlframestocsv.py; do
     echo
     f=$(echo $i | cut -f1 -d.)
     echo '##'
     echo "## $f"
     echo '##'
     python $D/$i -h
     echo
done | while read line; do
    echo "$line<br/>"
done | sed 's/[.]py//'

