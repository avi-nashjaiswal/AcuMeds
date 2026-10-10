# Shopkeeper Verification System

## Introduction
AcuMeds has a shopkeeper verification system to approve medical shop owners before they can use the platform.

## Problem
Earlier, shopkeeper registrations were not properly linked with the admin panel because of database mismatch.

## Definition
Verification means checking shopkeeper details like name, license, and contact information before approval.

## Problem Solution
The system now uses one shared database, and admins can approve or reject shopkeepers from the dashboard.

## Feasibility
This solution is feasible because it uses Flask, SQLite, SQLAlchemy, and simple admin workflows.

## Novelty and Innovation
The main innovation is a shared database with real-time verification sync between shopkeeper and admin portals.

## Project Objective
To create a secure and simple approval process for medical shopkeepers.

## Methodology
Shopkeeper registers, admin reviews the request, and verified shops get access to medicines and orders.

## System Architecture
Shopkeeper system, admin system, and customer system all connect to the same pharmacy.db database.

## Tools and Technique
Python, Flask, SQLite, SQLAlchemy, Bootstrap, and Jinja2 are used in this project.

## Conclusion
The verification system makes the platform more secure, organized, and reliable for all users.
