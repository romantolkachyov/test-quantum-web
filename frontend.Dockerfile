FROM node:18.13.0

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm install

COPY . .

CMD ["npm", "exec", "serve", "-s", "build"]
