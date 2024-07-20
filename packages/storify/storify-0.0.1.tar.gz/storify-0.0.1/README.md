# Storify

Storify is a lightweight Python-based database system that utilizes msgpack for efficient data serialization. It provides a robust framework for data storage and retrieval, with an optional ORM model for interaction with data. Storify supports automatic backups and error handling, ensuring data integrity and reliability. Easily create, rename, and remove databases while benefiting from a logging mechanism that tracks all operations.

## Features

- Create and manage multiple msgpack-based databases with ease.
- Lightweight ORM-esque model for easy interaction with data.
- Automatic backups and data flushing to prevent data loss.
- Built-in error handling to manage database corruption and loading issues.
- Configurable save intervals for optimized performance.

## Installation

```bash
pip install storify
```