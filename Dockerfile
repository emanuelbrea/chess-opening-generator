FROM public.ecr.aws/lambda/python:3.12

LABEL version="1.0"
LABEL authors="emanuel_brea"
LABEL description="Opening generator"

COPY ./requirements.txt ${LAMBDA_TASK_ROOT}


RUN pip install --no-cache-dir --upgrade -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY ./opening_generator ${LAMBDA_TASK_ROOT}/opening_generator
COPY ./config.toml ${LAMBDA_TASK_ROOT}

CMD ["opening_generator.application.handler"]