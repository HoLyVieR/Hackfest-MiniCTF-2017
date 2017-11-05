d = `pwd`
pushd ../CTFd/
cp $d/import.py ./
python import.py $d/data.json
popd

