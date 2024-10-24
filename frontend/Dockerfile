FROM node:22-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ENV REACT_APP_API_URL=https://chick-fil-ai.herokuapp.com/api
RUN npm run build

FROM node:22-slim AS production
RUN npm install -g serve
WORKDIR /app
COPY --from=build /app/build /app/build
CMD ["serve", "-s", "build", "-l", "${PORT:-3000}"]
