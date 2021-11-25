export PYSPARK_PYTHON=python3

#STOP HADOOP IF OPENED
sh script/stopHadoop.sh

#RUN HADOOP
sh script/runHadoop.sh

#RUN SPARK AND BUILD MODEL FOR PREDICTIONS
sh script/runSpark.sh

#RENAME XML TO PMML
cd output
mv part-00001 linreg.xml
mmv -v '*.xml' '#1.pmml'
cd ..

#LAUNCH OPENSCORING API
java -jar script/openscoring-server-executable-2.0.5.jar & 

#UPLOAD MODEL TO OPENSCORING
sleep 5
curl -X PUT --data-binary @output/linreg.pmml -H "Content-type: text/xml" http://localhost:8080/openscoring/model/linreg

#DISABLE CHROME SECURITY
google-chrome --disable-web-security --user-data-dir=[opt/google/chrome]


