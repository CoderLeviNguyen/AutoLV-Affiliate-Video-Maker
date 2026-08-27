import React from 'react';
import {
  AbsoluteFill,
  Html5Video,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const card = {
  background: 'rgba(0,0,0,0.68)',
  borderRadius: 28,
  padding: '26px 32px',
  boxShadow: '0 16px 40px rgba(0,0,0,0.28)',
};

export const AffiliateVertical = ({title, subtitle, price, voucher, cta, videoSrc}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const intro = spring({frame, fps, config: {damping: 16, stiffness: 120}});
  const ctaPulse = 1 + Math.sin(frame / 7) * 0.025;
  const subtitleOpacity = interpolate(frame, [8, 22], [0, 1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#111', color: '#fff', fontFamily: 'Arial, sans-serif'}}>
      {videoSrc ? (
        <Html5Video
          src={videoSrc}
          muted
          loop
          style={{width: '100%', height: '100%', objectFit: 'cover'}}
        />
      ) : (
        <AbsoluteFill
          style={{
            background: 'linear-gradient(160deg, #141414 0%, #292929 48%, #0f0f0f 100%)',
          }}
        />
      )}

      <AbsoluteFill
        style={{
          background: 'linear-gradient(180deg, rgba(0,0,0,.45) 0%, rgba(0,0,0,.05) 45%, rgba(0,0,0,.72) 100%)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          top: 110,
          left: 58,
          right: 58,
          transform: `translateY(${(1 - intro) * -55}px) scale(${0.94 + intro * 0.06})`,
          opacity: intro,
          ...card,
        }}
      >
        <div style={{fontSize: 62, fontWeight: 900, lineHeight: 1.08}}>{title}</div>
        <div style={{fontSize: 32, marginTop: 16, opacity: subtitleOpacity}}>{subtitle}</div>
      </div>

      <div style={{position: 'absolute', left: 58, right: 58, bottom: 250, display: 'grid', gap: 18}}>
        <div style={{...card, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div>
            <div style={{fontSize: 25, opacity: 0.8}}>Giá tham khảo</div>
            <div style={{fontSize: 62, fontWeight: 900}}>{price}</div>
          </div>
          <div style={{fontSize: 30, fontWeight: 800, textAlign: 'right'}}>{voucher}</div>
        </div>

        <div
          style={{
            borderRadius: 30,
            padding: '30px 34px',
            background: '#fff',
            color: '#111',
            fontSize: 38,
            fontWeight: 900,
            textAlign: 'center',
            transform: `scale(${ctaPulse})`,
          }}
        >
          {cta}
        </div>
      </div>
    </AbsoluteFill>
  );
};
