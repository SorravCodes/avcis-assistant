# AVCIS Architecture

## Objective
Build a local-first, internet-enabled personal assistant for Windows 11 and Android.

## Initial Architecture
- Windows hosts the primary Python application and local AI runtime.
- Android provides authorized device-control capabilities.
- Local models handle conversation and reasoning.
- Internet tools retrieve current web and YouTube information.
- SQLite and local files store memory and notes.
- LangChain and LangGraph support multi-step agent workflows.
- Sensitive and destructive actions require user confirmation.

## Storage Constraints
- Windows application target: maximum 10 GB.
- Android application target: maximum 5 GB.
- Actual installation sizes must be measured during development.

## Current Status
Task 1: Development environment and repository bootstrap.
