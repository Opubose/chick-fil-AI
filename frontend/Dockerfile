FROM node:22.9-alpine AS build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM node:22.9-alpine AS production

RUN npm install -g serve

WORKDIR /app

COPY --from=build /app/build /app/build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
