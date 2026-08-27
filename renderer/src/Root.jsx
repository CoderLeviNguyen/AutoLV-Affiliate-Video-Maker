import React from 'react';
import {Composition} from 'remotion';
import {AffiliateVertical} from './AffiliateVertical';

export const Root = () => (
  <Composition
    id="AffiliateVertical"
    component={AffiliateVertical}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={450}
    defaultProps={{
      title: 'Sản phẩm đáng thử hôm nay',
      subtitle: 'Giá tốt • Ưu đãi hấp dẫn',
      price: '199.000đ',
      voucher: 'Voucher đến 20%',
      cta: 'Xem link sản phẩm ngay',
      videoSrc: '',
    }}
  />
);
