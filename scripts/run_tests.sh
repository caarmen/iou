rm -rf reports
python -m pytest --cov=iou  --cov-report=xml --cov-report=html --junitxml="reports/junit.xml" iou/tests
mkdir -p reports
mv coverage.xml htmlcov reports/.
