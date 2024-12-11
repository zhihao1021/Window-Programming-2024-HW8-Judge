import User from "./user"

export default interface JWTData extends User {
    exp: number
};
