import React, { useState, useEffect } from 'react';
import './AlertMessaging.css';

const AlertMessaging = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sendingStatus, setSendingStatus] = useState({});
  const [selectedAlerts, setSelectedAlerts] = useState([]);
  const [customMessage, setCustomMessage] = useState('');
  const [sendToFarmers, setSendToFarmers] = useState(true);
  const [sendToAdmin, setSendToAdmin] = useState(true);

  // Descriptions des alertes météo (traduites en français)
  const ALERT_DESCRIPTIONS = {
    "Strong Wind": "Vent fort. Attachez ou couvrez vos cultures et mettez-les en sécurité.",
    "Extreme Heat": "Très chaud. Arrosez vos cultures et restez à l'ombre.",
    "Heavy Rain": "Pluie forte. Vérifiez les chemins d'eau et couvrez les jeunes cultures.",
    "Cold Temperatures": "Temps froid. Couvrez les cultures pour les garder au chaud.",
    "Extreme Cold": "Froid extrême. Protégez vos cultures du gel.",
    "Storm": "Tempête. Ne sortez pas et protégez votre ferme.",
    "Dryness Alert": "Alerte sécheresse. Augmentez l'arrosage de vos cultures."
  };

  // Descriptions des alertes parasitaires
  const PEST_ALERT_DESCRIPTIONS = {
    "Fall Armyworm": "Développement de la chenille légionnaire due aux conditions environnementales. Surveillez vos cultures pour détecter les dégâts foliaires et prenez des mesures préventives.",
    "Aphids": "Activité possible des pucerons due aux conditions environnementales. Inspectez les résidus collants sur les feuilles et envisagez des mesures de traitement appropriées.",
    "Stem Borers": "Risque de foreurs de tiges due aux conditions environnementales. Inspectez les tiges pour détecter les trous ou les dégâts et mettez en œuvre les actions correctives nécessaires.",
    "Corn Earworm": "Risque de ver de l'épi de maïs due aux conditions environnementales. Effectuez des inspections ponctuelles pour vérifier les tunnels dans les grains et prenez des mesures correctives.",
    "Black Cutworm": "Risque de ver gris noir due aux conditions environnementales. Vérifiez les trous d'alimentation dans les feuilles, les tiges coupées, les plantes flétries et prenez des mesures correctives.",
    "Peach Twig Borer": "Risque de foreur des rameaux de pêcher due aux conditions environnementales. Effectuez des inspections ponctuelles pour détecter le flétrissement des jeunes plantes.",
    "Coffee Berry Borer": "Développement du scolyte du grain de café due aux conditions environnementales. Vérifiez la chute des fruits des jeunes cerises vertes et inspectez les cerises sur les branches."
  };

  // Récupérer les alertes depuis l'API
  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/alerts');
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des alertes');
      }
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Erreur:', error);
      alert('Erreur lors de la récupération des alertes');
    } finally {
      setLoading(false);
    }
  };

  // Envoyer un SMS à un numéro spécifique
  const sendSMS = async (phone, message) => {
    try {
      const response = await fetch('/api/notifications/sms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: phone,
          message: message
        })
      });

      return response.ok;
    } catch (error) {
      console.error('Erreur envoi SMS:', error);
      return false;
    }
  };

  // Envoyer des alertes sélectionnées
  const sendSelectedAlerts = async () => {
    if (selectedAlerts.length === 0) {
      alert('Veuillez sélectionner au moins une alerte à envoyer');
      return;
    }

    setSendingStatus({ ...sendingStatus, sending: true });
    const adminPhone = "256783130358";
    let successCount = 0;
    let totalSent = 0;

    for (const alertIndex of selectedAlerts) {
      const alert = alerts[alertIndex];
      if (!alert) continue;

      // Construire le message pour les alertes météo
      let messages = [];
      
      if (alert.weather_alerts && alert.weather_alerts.length > 0) {
        for (const weatherAlert of alert.weather_alerts) {
          let message = `ALERTE MÉTÉO pour votre ferme: ${alert.farm.name}\n`;
          message += `Heure: ${weatherAlert.time}\n`;
          message += `Alertes: ${weatherAlert.alerts.join(', ')}\n`;

          // Ajouter les conseils
          for (const alertType of weatherAlert.alerts) {
            if (ALERT_DESCRIPTIONS[alertType]) {
              message += `Conseil: ${ALERT_DESCRIPTIONS[alertType]}\n`;
            }
          }

          // Ajouter les valeurs météo
          message += `Temp: ${weatherAlert.temperature}°C\n`;
          message += `Humidité: ${weatherAlert.humidity}%\n`;
          message += `Pluie: ${weatherAlert.precipitation} mm\n`;
          message += `Vent: ${weatherAlert.wind_speed} km/h`;

          messages.push(message);
        }
      }

      // Construire le message pour les alertes parasitaires
      if (alert.pest_alerts && alert.pest_alerts.length > 0) {
        for (const pestAlert of alert.pest_alerts) {
          for (const pest of pestAlert.alerts) {
            const description = PEST_ALERT_DESCRIPTIONS[pest];
            if (description) {
              const message = `ALERTE PARASITAIRE pour votre ferme: ${alert.farm.name}. ${description}`;
              messages.push(message);
            }
          }
        }
      }

      // Ajouter le message personnalisé si présent
      if (customMessage.trim()) {
        messages.unshift(customMessage.trim());
      }

      const finalMessage = messages.join('\n\n');

      // Liste des destinataires
      const recipients = [];
      
      if (sendToAdmin) {
        recipients.push(adminPhone);
      }
      
      if (sendToFarmers) {
        if (alert.farm.phonenumber) {
          recipients.push(alert.farm.phonenumber);
        }
        // Si vous avez un deuxième numéro de téléphone, décommentez la ligne suivante
        // if (alert.farm.phonenumber2) {
        //   recipients.push(alert.farm.phonenumber2);
        // }
      }

      // Envoyer aux destinataires
      for (const phone of recipients) {
        totalSent++;
        const success = await sendSMS(phone, finalMessage);
        if (success) {
          successCount++;
        }
        
        // Petite pause entre les envois
        await new Promise(resolve => setTimeout(resolve, 500));
      }
    }

    setSendingStatus({
      sending: false,
      completed: true,
      success: successCount,
      total: totalSent
    });

    setTimeout(() => {
      setSendingStatus({});
    }, 5000);
  };

  // Sélectionner/désélectionner une alerte
  const toggleAlert = (index) => {
    setSelectedAlerts(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  // Sélectionner toutes les alertes
  const selectAllAlerts = () => {
    if (selectedAlerts.length === alerts.length) {
      setSelectedAlerts([]);
    } else {
      setSelectedAlerts(alerts.map((_, index) => index));
    }
  };

  // Charger les alertes au montage du composant
  useEffect(() => {
    fetchAlerts();
    
    // Actualiser automatiquement toutes les 5 minutes
    const interval = setInterval(fetchAlerts, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="alert-messaging">
      <div className="header">
        <h2>🚨 Système d'Alertes Agricoles</h2>
        <div className="controls">
          <button 
            onClick={fetchAlerts} 
            disabled={loading}
            className="refresh-btn"
          >
            {loading ? '⟳ Chargement...' : '🔄 Actualiser'}
          </button>
        </div>
      </div>

      {/* Configuration d'envoi */}
      <div className="send-config">
        <h3>Configuration d'envoi</h3>
        <div className="config-options">
          <label>
            <input
              type="checkbox"
              checked={sendToAdmin}
              onChange={(e) => setSendToAdmin(e.target.checked)}
            />
            Envoyer à l'administrateur
          </label>
          <label>
            <input
              type="checkbox"
              checked={sendToFarmers}
              onChange={(e) => setSendToFarmers(e.target.checked)}
            />
            Envoyer aux fermiers
          </label>
        </div>
        
        <div className="custom-message">
          <label>Message personnalisé (optionnel):</label>
          <textarea
            value={customMessage}
            onChange={(e) => setCustomMessage(e.target.value)}
            placeholder="Ajoutez un message personnalisé qui sera envoyé avec les alertes..."
            rows={3}
          />
        </div>
      </div>

      {/* Actions de sélection */}
      <div className="selection-controls">
        <button 
          onClick={selectAllAlerts}
          className="select-all-btn"
          disabled={alerts.length === 0}
        >
          {selectedAlerts.length === alerts.length ? 'Tout désélectionner' : 'Tout sélectionner'}
        </button>
        
        <span className="selection-info">
          {selectedAlerts.length} / {alerts.length} alertes sélectionnées
        </span>
        
        <button 
          onClick={sendSelectedAlerts}
          disabled={selectedAlerts.length === 0 || sendingStatus.sending || (!sendToAdmin && !sendToFarmers)}
          className="send-btn"
        >
          {sendingStatus.sending ? '📤 Envoi en cours...' : `📱 Envoyer (${selectedAlerts.length})`}
        </button>
      </div>

      {/* Statut d'envoi */}
      {sendingStatus.completed && (
        <div className={`status-message ${sendingStatus.success === sendingStatus.total ? 'success' : 'warning'}`}>
          ✅ Envoi terminé: {sendingStatus.success}/{sendingStatus.total} messages envoyés avec succès
        </div>
      )}

      {/* Liste des alertes */}
      <div className="alerts-container">
        {loading ? (
          <div className="loading">Chargement des alertes...</div>
        ) : alerts.length === 0 ? (
          <div className="no-alerts">
            <p>🌟 Aucune alerte active actuellement</p>
            <p>Toutes vos fermes sont en sécurité !</p>
          </div>
        ) : (
          <div className="alerts-grid">
            {alerts.map((alert, index) => (
              <div 
                key={`${alert.farm.id}-${index}`}
                className={`alert-card ${selectedAlerts.includes(index) ? 'selected' : ''}`}
                onClick={() => toggleAlert(index)}
              >
                <div className="alert-header">
                  <input
                    type="checkbox"
                    checked={selectedAlerts.includes(index)}
                    onChange={() => toggleAlert(index)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <h4>🏡 {alert.farm.name}</h4>
                  <span className="location">📍 {alert.farm.geolocation}</span>
                </div>

                <div className="alert-content">
                  {/* Alertes météo */}
                  {alert.weather_alerts && alert.weather_alerts.length > 0 && (
                    <div className="weather-alerts">
                      <h5>🌤️ Alertes Météo</h5>
                      {alert.weather_alerts.map((weatherAlert, wIndex) => (
                        <div key={wIndex} className="weather-alert">
                          <div className="alert-time">⏰ {weatherAlert.time}</div>
                          <div className="alert-types">
                            {weatherAlert.alerts.map((alertType, aIndex) => (
                              <span key={aIndex} className={`alert-tag ${alertType.toLowerCase().replace(' ', '-')}`}>
                                {alertType}
                              </span>
                            ))}
                          </div>
                          <div className="weather-details">
                            <span>🌡️ {weatherAlert.temperature}°C</span>
                            <span>💧 {weatherAlert.humidity}%</span>
                            <span>🌧️ {weatherAlert.precipitation}mm</span>
                            <span>💨 {weatherAlert.wind_speed}km/h</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Alertes parasitaires */}
                  {alert.pest_alerts && alert.pest_alerts.length > 0 && (
                    <div className="pest-alerts">
                      <h5>🐛 Alertes Parasitaires</h5>
                      {alert.pest_alerts.map((pestAlert, pIndex) => (
                        <div key={pIndex} className="pest-alert">
                          <div className="alert-time">⏰ {pestAlert.time}</div>
                          <div className="pest-info">
                            <span>🌡️ GDD: {pestAlert.gdd}</span>
                            <span>🌡️ Temp: {pestAlert.temperature}°C</span>
                          </div>
                          <div className="pest-types">
                            {pestAlert.alerts.map((pest, pIndex) => (
                              <span key={pIndex} className="pest-tag">
                                🐛 {pest}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Contact Info */}
                  {alert.farm.phonenumber && (
                    <div className="contact-info">
                      <span>📞 {alert.farm.phonenumber}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AlertMessaging;
