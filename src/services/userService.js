import UserModel from "../models/userModel.js";

const UserService = {
  createUser: async (name, email) => {
    return await UserModel.createUser(name, email);
  },

  getAllUsers: async () => {
    return await UserModel.getAllUsers();
  },

  getUserById: async (id) => {
    return await UserModel.getUserById(id);
  },
};

export default UserService;
