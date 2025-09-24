# Cloud-Project-101
Semester 5 Project : Serverless Resume Parser and Job Notifier 

This project is an event-driven serverless application built on AWS, designed to meet the requirements of a cloud computing assignment. The application provides a simple web interface for candidates to upload resumes and for an HR user to post new job openings. The backend automatically parses resumes for skills and notifies matching candidates when a relevant job is posted.

Architecture Overview
The application is built using a decoupled, serverless architecture. The primary AWS services used are:

1.Amazon S3:For storing uploaded resume files.
2.AWS Lambda: For all the compute logic, including handling API requests, parsing resumes, and sending notifications.
3.Amazon API Gateway: Provides a secure RESTful API for the web application.
4.Amazon DynamoDB: A  NoSQL database for storing structured data about candidates and jobs.
5.Amazon SNS (Simple Notification Service): Acts as a message bus to decouple the job posting process from the notification logic.
6.Amazon Textract: To automatically extract text from resume documents.
7.Amazon CloudWatch: For real-time logging and monitoring of all backend processes.
