import { IUser } from "@/modules/types";
import Axios from "axios";
import CrudService from "./crud";

/** Users service */
export default class UsersService extends CrudService<IUser> {
  constructor() {
    super("/users");
  }

  /**
   * Change password for specified user.
   * @param user User to change password for.
   * @param password New password.
   */
  public async changePassword(user: IUser, password: string) {
    const url = `${this.url}/${user.oid}/changePassword`;
    const res = await Axios.put(url, { password });
    return res.data;
  }
}
