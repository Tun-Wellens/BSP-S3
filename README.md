# Endless Cyclist

## Overview
Endless Cyclist is an endless runner game developed using Pygame, where the player controls a cyclist navigating through lanes while avoiding incoming obstacles (cars). The game progressively increases in difficulty, ensuring an engaging and challenging experience.

## Features
- **Three-lane road** for dynamic movement
- **Controlled randomness** ensuring there is an open path
- **Animated cyclist** to simulate pedaling
- **Dynamic difficulty scaling** as the score increases
- **Collision detection** triggering game-over sequence
- **Sound effects and music** for enhanced experience

## Installation
1. Install Python (if not already installed)
2. Install required dependencies:
   ```sh
   pip install pygame
   ```
3. Run the game:
   ```sh
   python main.py
   ```

## Controls
- **Left Arrow (`←`)** - Move left
- **Right Arrow (`→`)** - Move right

## Game Mechanics
- The player starts in the middle lane.
- Cars spawn randomly in lanes, progressively increasing in frequency.
- The cyclist must dodge incoming cars by switching lanes.
- Collision with a car ends the game.
- Score increases over time, affecting difficulty level.

## Assets Used
- **Player Sprites**: `player1.png`, `player2.png`
- **Background**: `background.png`
- **Obstacles**: `carRed.png`
- **Sound Effects**: `crash_sound.wav`, `game_music.mp3`, `game_over_music.mp3`
