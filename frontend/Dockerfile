# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory to /app
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React app
RUN npm run build

# Install serve to run the static files
RUN npm install -g serve

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run serve command to serve the static files
CMD ["serve", "-s", "build"]
