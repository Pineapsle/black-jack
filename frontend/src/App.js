import React, { useEffect, useState } from 'react';
import './App.css';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000'); // Connect to backend

function App() {
  const [connected, setConnected] = useState(false);
  const [playerHand, setPlayerHand] = useState([]);
  const [dealerHand, setDealerHand] = useState([]);
  const [playerScore, setPlayerScore] = useState(0);
  const [dealerScore, setDealerScore] = useState(null);
  const [gameOverMessage, setGameOverMessage] = useState('');

  useEffect(() => {
    socket.on('connect', () => {
      setConnected(true);
      console.log('Connected to the server');
      socket.emit('join_game');
    });

    socket.on('disconnect', () => {
      setConnected(false);
      console.log('Disconnected from the server');
    });

    socket.on('game_joined', (data) => {
      setPlayerHand(data.playerHand);
      setDealerHand(data.dealerHand);
      setPlayerScore(data.playerScore);
      setDealerScore(data.dealerScore);
      setGameOverMessage('');
    });

    socket.on('update', (data) => {
      console.log("Received update:", data);
      setPlayerHand(data.playerHand);
      setPlayerScore(data.playerScore);
    });

    socket.on('game_over', (data) => {
      setPlayerHand(data.playerHand);
      setDealerHand(data.dealerHand || []);
      setPlayerScore(data.playerScore);
      setDealerScore(data.dealerScore || null);
      setGameOverMessage(data.message);
    });

    return () => {
      socket.off('connect');
      socket.off('disconnect');
      socket.off('game_joined');
      socket.off('update');
      socket.off('game_over');
    };
  }, []);

  const handleHit = () => {
    console.log("Hit button clicked");
    socket.emit('hit');
  };

  const handleStand = () => {
    socket.emit('stand');
  };

  const renderHand = (hand) => (
    <div className="hand">
      {hand.map((card, index) => (
        <div key={index} className="card">
          <span>{card[0]}</span>
          <span className="suit">{card[1]}</span>
        </div>
      ))}
    </div>
  );

  return (
    <div className="App">
      <h1>♠ Blackjack Game ♣</h1>
      <p className={`status ${connected ? 'connected' : 'disconnected'}`}>
        {connected ? "Connected to server" : "Not connected"}
      </p>

      <div className="game-area">
        <div className="player-section">
          <h2>Player</h2>
          {renderHand(playerHand)}
          <p className="score">Score: {playerScore}</p>
        </div>

        <div className="dealer-section">
          <h2>Dealer</h2>
          {renderHand(dealerHand)}
          {dealerScore !== null && <p className="score">Score: {dealerScore}</p>}
        </div>
      </div>

      <div className="controls">
        <button onClick={handleHit} disabled={!!gameOverMessage}>Hit</button>
        <button onClick={handleStand} disabled={!!gameOverMessage}>Stand</button>
      </div>

      {gameOverMessage && (
        <div className="result">
          <h2>{gameOverMessage}</h2>
          <button className="play-again" onClick={() => socket.emit('join_game')}>Play Again</button>
        </div>
      )}
    </div>
  );
}

export default App;
