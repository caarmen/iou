rm -rf reports
python -m manage collectstatic --noinput
python -m pytest --cov=iou --cov=iouproject --cov-report=xml --cov-report=html --junitxml="reports/junit.xml"
mkdir -p reports
mv coverage.xml htmlcov reports/.
