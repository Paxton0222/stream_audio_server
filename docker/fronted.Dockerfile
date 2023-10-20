# Use the official Node.js image as the base image
FROM node:18

ARG env_mode
ENV ENV_MODE=$env_mode

# Create and set the working directory in the container
WORKDIR /app

# Copy the package.json and package-lock.json to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the app files to the container
COPY . .

# Build the Vue 3 app
RUN npm run build -- --mode $ENV_MODE

EXPOSE 4173

# Start the Vue 3 app
CMD [ "npm", "run", "preview" ]
