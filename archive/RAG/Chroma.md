Vector Embedding: check leaderboard for the best https://huggingface.co/spaces/mteb/leaderboard 
Analyzing the data: Similarity search algorithms like nearest neighbor: cosine similarity, Manhatten search and Euclidean distance, Range search (recommendation systems), Filtering by metadata

Implementing Chroma DB: A summarized step-by-step process
1. Get embeddings: Take the actions needed to convert words, images, or data into numbers and, specifically, vector representations.
2. Create collections: Create collections to group data like tables in a relational database.
3. Put data into collections: Save the data, like text and embeddings, in collections after preprocessing the data and generating vector embeddings.
4. Perform collection operations: Use Chroma DB to delete, change, or rename collections, among other actions, which gives you more ways to work with your data.
5. Use text or vector searches to find information to locate your answers based on semantic meaning or vector similarity, which is a useful way to get the most out of your data.


docker run -p 8000:8000 chromadb/chroma

docker run This command creates the Docker environment which is needed to pull images and then configure environments.

p 8000:8000 This code specifies that port 8000 on left side is for the container, which then maps to port 8000 on right side of your host machine.

chromadb/chroma This instruction tells Docker which image needs to pull. In this instance, the Chroma database program in the chromadb/chroma image is in use.

npm install chromadb

add file in directory: After performing above step, a pop-up box displays with default file name Untitled.txt as shown in the following screenshot. Replace its default name with chromaData.js.

Task 3: Create a Collection and Embed Data

First, import the ChromaClient class from the chromadb package. You will use this class to create an instance of the client that interacts with the Chroma DB database. To import the ChromaClient, you must use the required keyword of “chromadb”. You include this command in your Javascript file.


const { ChromaClient } = require('chromadb');
const client = new ChromaClient();


2. Next, create the main asynchronous function. This code block also contains the code for interacting with the Chroma DB database.

async function main() {
  try {
  } catch (error) {
    console.error("Error:", error);
  }
}

3. Then, create a collection inside the database. For this task you will construct the collection inside the try block of the main function.

The following code retrieves or creates a collection named "my_basic_collection" from the database using the client's getOrCreateCollection method. This code makes sure that a collection exists in the database, either by getting an existing collection or by creating a new collection if the collection does not exist. The collection variable holds a reference to this collection for further operations.


const collection = await client.getOrCreateCollection({
name: "my_basic_collection"
});


4. Next, define an array named "texts" containing sample text string data. Use the following code to construct your sample text string data.

const texts = [
      "This is sample text 1.",
      "This is sample text 2.",
      "This is sample text 3."
];
Copied!
Then, generate unique identifers, or IDs for each text item in the array. To complete this task, the following code generates unique IDs for the documents based on their index in the text array.

Each ID has the format document_<index>, where <index> starts from 1.
The add method calls the collection object to add documents to the collection.
This coding method takes an object with IDs and document properties. Ids contain an array of document IDs, and documents contain an array of corresponding document texts.
1
const ids = texts.map((_, index) => `document_${index + 1}`);
Copied!
Next, add the data and IDs to your created collection.

1
2
 await collection.add({ ids: ids, documents: texts });
 ```
Copied!
Finally, you can retrieve all items that are in the collection using the get method. The result logs to the console for verification.

1
2
const allItems = await collection.get();
console.log(allItems);
Copied!
To view the output, you need to call the main function.

1
main()

Task 4: Check the Output
View the output so that you can verify that the collection includes the data.

Verify that the terminal in which you execute Docker command is still running.

In the terminal window, perform the given command to see the output.

1
node chromaData.js

const { ChromaClient } = require('chromadb');
const client = new ChromaClient();

async function main() {
    try {
        const collection = await client.getOrCreateCollection({
            name: "my_basic_collection"
        });

        const texts = [
            "This is sample text 1.",
            "This is sample text 2.",
            "This is sample text 3."
        ];

        const ids = texts.map((_, index) => `document_${index + 1}`);

        await collection.add({ ids: ids, documents: texts });

        const allItems = await collection.get();
        console.log(allItems);
    } catch (error) {
        console.error("Error:", error);
    }
}

main().catch(console.error);

Moved all asynchronous operations inside the main function.
Changed document to documents in the collection.add() call, as the ChromaDB API expects documents (plural) for multiple items.
Added a main().catch(console.error) at the end to properly handle any unhandled promise rejections.