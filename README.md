# Home Assistant Control Panel

A lightweight Flask dashboard for browsing and controlling Home Assistant entities through the REST API.

## Features

- Local-first setup
- Works with your own Home Assistant URL and token
- Demo mode for safe screenshots and quick testing
- Browse entities grouped by domain
- Search by friendly name or entity ID
- Filter by domain
- Optional "available only" filter
- Turn supported entities on and off (`light`, `switch`, `fan`)

## Why this project exists

This project is meant to be a simple, clean alternative for quickly browsing and controlling Home Assistant entities from a small local dashboard.

It is designed to run locally on your own machine, so your Home Assistant token stays under your control.

## Quick start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/home-assistant-control-panel.git
cd home-assistant-control-panel
