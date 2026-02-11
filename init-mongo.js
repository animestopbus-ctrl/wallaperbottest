#!/usr/bin/env node

// Initialize MongoDB database for LastPerson07Bot
console.log('Initializing MongoDB...');

// Check if database exists
const { MongoClient } = require('mongodb');
const { ServerApiVersion } = require('mongodb');
const client = new MongoClient(process.env.MONGODB_URI);

try {
    // Connect to MongoDB
    await client.connect();
    const db = client.db('lastperson07_bot');
    console.log('Connected to MongoDB successfully!');
    
    // Check if collections exist
    const collections = await db.listCollections().toArray();
    console.log(`Found ${collections.length} existing collections`);
    
    if (!collections.includes('users')) {
        console.log('Database does not exist. Creating collections...');
        
        // Create indexes for better performance
        await db.users.createIndex({_id: 1}, {unique: true});
        await db.users.createIndex({'username': 1}, {sparse: true});
        await db.users.createIndex({'tier': 1});
        await db.users.createIndex({'banned': 1});
        await db.users.createIndex({'join_date': 1});
        
        await db.createCollection('api_urls');
        await db.api_urls.createIndex({url: 1}, {unique: true});
        await db.api_urls.createIndex({'source_name': 1});
        
        await db.createCollection('schedules');
        await db.schedules.createIndex({'chat_id': 1, 'category': 1}, {unique: true});
        await db.schedules.createIndex({'last_post_time': 1});
        
        await db.createCollection('bot_settings');
        await db.bot_settings.createIndex({'key': 1}, {unique: true});
        
        await db.createCollection('logs');
        await db.logs.createIndex({'timestamp': 1});
        await db.logs.createIndex({'level': 1});
        
        console.log('Database initialized successfully!');
    }
    
    catch (error) {
        console.error('MongoDB initialization error:', error.message);
    } finally {
        if (client) {
            await client.close();
        }
        process.exit(0);
