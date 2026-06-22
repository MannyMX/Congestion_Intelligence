FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
# In case package.json doesn't exist yet during initial build attempt, we do a conditional install
RUN if [ -f package.json ]; then npm install; fi

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]
