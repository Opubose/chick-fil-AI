FROM node:23-slim AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM node:23-slim AS production

RUN npm install -g serve

WORKDIR /app

COPY --from=build /app/build /app/build

CMD ["serve", "-s", "build", "-l", "3000"]
