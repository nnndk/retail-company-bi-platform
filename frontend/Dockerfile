# Use the official Node.js image as the base image
FROM node:14-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React application
RUN npm run build

# Serve the application using a simple server
# You can also use serve if you have it in your package.json
RUN npm install -g serve

# Expose port 5000
EXPOSE 3000

# Command to run the application
CMD ["serve", "-s", "build", "-l", "3000"]