package org.opensky.tools;

import lombok.Getter;

/**
 * Represents a bounding box of WGS84 coordinates (decimal degrees) that encompasses a certain area. It is
 * defined by a lower and upper bound for latitude and longitude.
 */

@Getter
public class BoundingBox {
    private double minLatitude;
    private double minLongitude;
    private double maxLatitude;
    private double maxLongitude;

    /**
     * Create a bounding box, given the lower and upper bounds for latitude and longitude.
     */
    public BoundingBox(double minLatitude, double maxLatitude,  double minLongitude, double maxLongitude) {
        checkLatitude(minLatitude);
        checkLatitude(maxLatitude);
        checkLongitude(minLongitude);
        checkLongitude(maxLongitude);

        this.minLatitude = minLatitude;
        this.minLongitude = minLongitude;
        this.maxLatitude = maxLatitude;
        this.maxLongitude = maxLongitude;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof BoundingBox)) return false;

        BoundingBox that = (BoundingBox) o;

        if (Double.compare(that.minLatitude, minLatitude) != 0) return false;
        if (Double.compare(that.minLongitude, minLongitude) != 0) return false;
        if (Double.compare(that.maxLatitude, maxLatitude) != 0) return false;
        return Double.compare(that.maxLongitude, maxLongitude) == 0;
    }

    @Override
    public int hashCode() {
        int result;
        long temp;
        temp = Double.doubleToLongBits(minLatitude);
        result = (int) (temp ^ (temp >>> 32));
        temp = Double.doubleToLongBits(minLongitude);
        result = 31 * result + (int) (temp ^ (temp >>> 32));
        temp = Double.doubleToLongBits(maxLatitude);
        result = 31 * result + (int) (temp ^ (temp >>> 32));
        temp = Double.doubleToLongBits(maxLongitude);
        result = 31 * result + (int) (temp ^ (temp >>> 32));
        return result;
    }

    private void checkLatitude(Double lat) {
        if (lat < -90 || lat > 90) throw new RuntimeException(String.format("Illegal latitude %f. Must be within [-90, 90]", lat));
    }

    private void checkLongitude(Double lon) {
        if (lon < -180 || lon > 180) throw new RuntimeException(String.format("Illegal longitude %f. Must be within [-90, 90]", lon));
    }
}
