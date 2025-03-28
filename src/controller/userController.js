import UserService from "../services/userService.js";
import { successResponse, errorResponse } from "../utils/response.js";

const UserController = {
  createUser: async (req, res) => {
    try {
      const { name, email } = req.body;
      const user = await UserService.createUser(name, email);
      successResponse(res, "User created successfully", user);
    } catch (error) {
      errorResponse(res, error.message);
    }
  },

  getAllUsers: async (req, res) => {
    try {
      const users = await UserService.getAllUsers();
      successResponse(res, "Users fetched successfully", users);
    } catch (error) {
      errorResponse(res, error.message);
    }
  },

  getUserById: async (req, res) => {
    try {
      const user = await UserService.getUserById(req.params.id);
      if (user) {
        successResponse(res, "User fetched successfully", user);
      } else {
        errorResponse(res, "User not found", 404);
      }
    } catch (error) {
      errorResponse(res, error.message);
    }
  },
};

export default UserController;
