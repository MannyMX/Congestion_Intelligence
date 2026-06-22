export default function Sidebar({ zones, loading }: { zones: any[], loading: boolean }) {
  const getSeverityClass = (score: number) => {
    if (score > 0.7) return 'high-severity';
    if (score > 0.4) return 'medium-severity';
    return 'low-severity';
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Enforcement Priorities</h2>
        <p>Ranked hotspots requiring immediate attention</p>
      </div>
      
      <div className="zone-list">
        {loading ? (
          <div className="loading-spinner">Analyzing zones...</div>
        ) : (
          zones.map((zone) => (
            <div key={zone.zone_id} className={`zone-card ${getSeverityClass(zone.score)}`}>
              <div className="zone-header">
                <div className="zone-title">{zone.police_station} Area</div>
                <div className="zone-score">{zone.score.toFixed(2)}</div>
              </div>
              <div className="zone-details">
                <div className="detail-row">
                  <span className="detail-label">Violations</span>
                  <span className="detail-value">{zone.violation_count}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Primary Issue</span>
                  <span className="detail-value" style={{maxWidth: '150px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}} title={zone.dominant_violation_tag}>
                    {zone.dominant_violation_tag}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Vehicle Profile</span>
                  <span className="detail-value">{zone.dominant_vehicle_type}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
