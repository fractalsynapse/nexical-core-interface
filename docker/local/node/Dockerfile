FROM node:22-bullseye-slim

WORKDIR /node-lib

COPY ./docker/package.json /node-lib

RUN npm install --prefix=/node-lib && npm cache clean --force

ENV PATH=/node-lib/node_modules/.bin/:$PATH
ENV NODE_PATH=/node-lib/node_modules

WORKDIR /app
